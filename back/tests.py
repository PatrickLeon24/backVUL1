from django.test import TestCase, Client
from django.urls import reverse
from back.models import Tipo_Usuario, CodigoInvitacion, Usuario , Token, Cupon, GestorCupon, Notificacion
from back.services.gestor_cupon_service import GestorCuponService
from unittest.mock import patch
import json
from django.utils import timezone
from django.utils.timezone import now

class RegistrarUsuarioTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('registrar_usuario')

        # Crear tipos de usuario
        self.tipo_usuario_normal = Tipo_Usuario.objects.create(id=1, tipo="Usuario")
        self.tipo_usuario_admin = Tipo_Usuario.objects.create(id=2, tipo="Administrador")

        # Crear un usuario para asignar al campo `creado_por`
        self.creador = Usuario.objects.create(nombre="pleon", email="admin@example.com", contrasena="securepassword", tipousuario=self.tipo_usuario_admin)

        # Crear un código de invitación válido
        self.codigo_invitacion = CodigoInvitacion.objects.create(
            codigo="INVI123",
            utilizado=False,
            creado_por=self.creador
        )

        # Crear un usuario existente para pruebas de correo duplicado
        self.usuario_existente = Usuario.objects.create(
            nombre="usuario_existente",
            email="test@example.com",
            contrasena="securepassword",
            tipousuario=self.tipo_usuario_normal
        )

    @patch('back.services.usuario_service.UsuarioService.crear_usuario')
    def test_usuario_normal_registrado_exitosamente(self, mock_crear_usuario):
        datos = {
            "email": "nuevo_usuario@example.com",
            "tipo_usuario": self.tipo_usuario_normal.id,
            "contrasena": "password123",
        }
        response = self.client.post(self.url, data=datos, content_type="application/json")

        self.assertEqual(response.status_code, 201)
        self.assertJSONEqual(response.content, {"mensaje": "Usuario registrado exitosamente"})
        mock_crear_usuario.assert_called_once_with(datos, self.tipo_usuario_normal)

    def test_email_ya_registrado(self):
        datos = {
            "email": "test@example.com",  # Correo ya existente
            "tipo_usuario": self.tipo_usuario_normal.id,
            "contrasena": "password123",
        }
        response = self.client.post(self.url, data=datos, content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "El correo ya está registrado, ingrese uno nuevo"})

    def test_tipo_usuario_invalido(self):
        datos = {
            "email": "nuevo_usuario@example.com",
            "tipo_usuario": 999,  # ID inexistente
            "contrasena": "password123",
        }
        response = self.client.post(self.url, data=datos, content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Tipo de usuario no válido"})

    def test_contrasena_invalida(self):
        datos = {
            "email": "nuevo_usuario@example.com",
            "tipo_usuario": self.tipo_usuario_normal.id,
            "contrasena": "short",
        }
        response = self.client.post(self.url, data=datos, content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "La contraseña debe tener 8 caracteres como mínimo"})

    def test_codigo_invitacion_faltante_para_administrador(self):
        datos = {
            "email": "admin_nuevo@example.com",
            "tipo_usuario": self.tipo_usuario_admin.id,
            "contrasena": "password123",
        }
        response = self.client.post(self.url, data=datos, content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Se requiere un código de invitación para registrarse como administrador"})

    def test_codigo_invitacion_invalido_o_utilizado(self):
        datos = {
            "email": "admin_nuevo@example.com",
            "tipo_usuario": self.tipo_usuario_admin.id,
            "contrasena": "password123",
            "codigo_invitacion": "INVALIDO",
        }
        response = self.client.post(self.url, data=datos, content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Código de invitación inválido o ya utilizado"})

    @patch('back.services.usuario_service.UsuarioService.crear_usuario')
    def test_administrador_registrado_exitosamente(self, mock_crear_usuario):
        datos = {
            "email": "admin_nuevo@example.com",
            "tipo_usuario": self.tipo_usuario_admin.id,
            "contrasena": "password123",
            "codigo_invitacion": self.codigo_invitacion.codigo,
        }
        response = self.client.post(self.url, data=datos, content_type="application/json")

        self.assertEqual(response.status_code, 201)
        self.assertJSONEqual(response.content, {"mensaje": "Usuario registrado exitosamente"})
        
        # Asegurar que el código fue marcado como utilizado
        self.codigo_invitacion.refresh_from_db()
        self.assertTrue(self.codigo_invitacion.utilizado)
        mock_crear_usuario.assert_called_once_with(datos, self.tipo_usuario_admin)

    def test_metodo_no_permitido(self):
        response = self.client.get(self.url)  # Método GET en lugar de POST

        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {"error": "Método no permitido"})


# Pruebas (Edson)
class ObtenerPuntajeUsuarioTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Crear usuarios para las pruebas
        self.usuario_existente = Usuario.objects.create(
            id=1, nombre="Usuario Existente", email="usuario@example.com", puntaje_acumulado=150
        )
        self.usuario_inexistente_id = 999  # ID que no existe en la base de datos

    def test_puntaje_usuario_existente(self):
        url = reverse('obtener_puntaje_usuario', args=[self.usuario_existente.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'puntos': 150})

    def test_usuario_no_existente(self):
        url = reverse('obtener_puntaje_usuario', args=[self.usuario_inexistente_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {'error': 'Usuario no encontrado.'})

    def test_metodo_no_permitido(self):
        url = reverse('obtener_puntaje_usuario', args=[self.usuario_existente.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {'error': 'Método no permitido'})

    def test_error_interno(self):
        with self.assertRaises(Exception):
            url = reverse('obtener_puntaje_usuario', args=["cadena_invalida"])
            self.client.get(url)


class CrearPagoTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.valid_payload = {
            "estado": "Completado",
            "metodo_pago": "Tarjeta",
            "monto_pago": 150.00
        }
        self.invalid_payload = {
            "estado": "",
            "metodo_pago": "",
            "monto_pago": None
        }
        self.error_payload = {
            "estado": "Completado",
            "metodo_pago": "Tarjeta",
            "monto_pago": "cadena_invalida"
        }
        self.url = reverse('crear_pago')

    def test_crear_pago_exitoso(self):
        """Prueba que un pago válido se crea correctamente."""
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("pago_id", response.json())
        self.assertEqual(response.json().get("mensaje"), "Pago creado exitosamente")

    def test_crear_pago_con_datos_invalidos(self):
        """Prueba que se devuelve un error al enviar datos incompletos."""
        response = self.client.post(
            self.url,
            data=self.invalid_payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        self.assertEqual(response.json()["error"], "Faltan campos obligatorios")

    def test_metodo_no_permitido(self):
        """Prueba que el método GET no está permitido."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertIn("error", response.json())
        self.assertEqual(response.json()["error"], "Método no permitido")

    def test_error_interno(self):
        """Prueba que se manejen errores internos en el servidor."""
        response = self.client.post(
            self.url,
            data=self.error_payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json())
        self.assertTrue("monto inválido" in response.json()["error"].lower())


#Pruebas Patrick 
class EnviarTokenTests(TestCase):
    def setUp(self):
        self.url = reverse('enviar_token')
        self.usuario = Usuario.objects.create(
            nombre="Test", apellido="User", email="test@example.com", contrasena="password"
        )

    def test_enviar_token_usuario_existente(self):
        response = self.client.post(self.url, json.dumps({'correo': self.usuario.email}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Token enviado al correo del usuario.'})

    def test_enviar_token_usuario_no_existente(self):
        response = self.client.post(self.url, json.dumps({'correo': 'nonexistent@example.com'}), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {'error': 'Usuario no encontrado.'})

    def test_metodo_no_permitido(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {'error': 'Método no permitido'})


class CambiarContrasenaTests(TestCase):
    def setUp(self):
        self.url = reverse('cambiar_contrasena')
        self.usuario = Usuario.objects.create(
            nombre="Test", apellido="User", email="test@example.com", contrasena="password"
        )
        # Create a valid token for the user
        self.token = Token.objects.create(
            usuario=self.usuario,
            token='1234567890',
            activo=True,
            fecha_creacion=timezone.now()
        )

    def test_cambiar_contrasena_con_token_valido(self):
        response = self.client.post(self.url, json.dumps({
            'correo': self.usuario.email,
            'token': self.token.token,
            'nueva_contrasena': 'newpassword123'
        }), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Contraseña cambiada exitosamente.'})

        # Verify the password has been updated
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.contrasena, 'newpassword123')

        # Verify the token is deactivated
        self.token.refresh_from_db()
        self.assertFalse(self.token.activo)

    def test_cambiar_contrasena_con_token_invalido(self):
        response = self.client.post(self.url, json.dumps({
            'correo': self.usuario.email,
            'token': 'invalidtoken',
            'nueva_contrasena': 'newpassword123'
        }), content_type="application/json")
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Token no válido o caducado.'})

    def test_cambiar_contrasena_usuario_no_existente(self):
        response = self.client.post(self.url, json.dumps({
            'correo': 'nonexistent@example.com',
            'token': self.token.token,
            'nueva_contrasena': 'newpassword123'
        }), content_type="application/json")
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Usuario no encontrado.'})

    def test_cambiar_contrasena_contrasena_insegura(self):
        response = self.client.post(self.url, json.dumps({
            'correo': self.usuario.email,
            'token': self.token.token,
            'nueva_contrasena': 'short'
        }), content_type="application/json")
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'La contraseña nueva no cumple los requisitos de seguridad.'})

    def test_metodo_no_permitido(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {'error': 'Método no permitido'})

#Pruebas ITalo 
class CanjearCuponTests(TestCase):

    def setUp(self):
        # Crear un usuario de prueba
        self.usuario = Usuario.objects.create(
            id=1,
            nombre="Test",
            apellido="User",
            email="usuario@example.com",
            contrasena="password",
            puntaje_acumulado=1000,
        )

        # Crear un cupón de prueba
        self.cupon = Cupon.objects.create(
            id=1,
            local="KFC",
            costo_puntos=900,
            disponibilidad=5,
            descripcion="Cupon de descuento KFC",
            descuento=20,
            imagen="https://KFClogo.com"
        )

    def test_usuario_no_existe(self):
        response = GestorCuponService.canjear_cupon(usuario_id=999, cupon_id=self.cupon.id)  # Usuario inexistente
        self.assertEqual(response, {'error': 'Usuario no encontrado'})

    def test_cupon_no_existe(self):
        response = GestorCuponService.canjear_cupon(usuario_id=self.usuario.id, cupon_id=999)  # Cupón inexistente
        self.assertEqual(response, {'error': 'Cupón no encontrado'})

    def test_cupon_puntos_insuficientes(self):
        self.usuario.puntaje_acumulado = 500  # Puntos insuficientes
        self.usuario.save()

        response = GestorCuponService.canjear_cupon(usuario_id=self.usuario.id, cupon_id=self.cupon.id)
        self.assertEqual(response, {'error': 'Puntos insuficientes para canjear el cupón'})

    def test_cupon_sin_disponibilidad(self):
        self.cupon.disponibilidad = 0  # Sin disponibilidad
        self.cupon.save()

        response = GestorCuponService.canjear_cupon(usuario_id=self.usuario.id, cupon_id=self.cupon.id)
        self.assertEqual(response, {'error': 'El cupón ya no está disponible'})

    def test_canje_exitoso(self):
        response = GestorCuponService.canjear_cupon(usuario_id=self.usuario.id, cupon_id=self.cupon.id)

        # Verificar respuesta
        self.assertIn('mensaje', response)
        self.assertEqual(response['mensaje'], 'Canje exitoso')
        self.assertIn('url_qr', response)

        # Verificar actualizaciones en el usuario
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.puntaje_acumulado, 100)  # 1000 - 900

        # Verificar actualizaciones en el cupón
        self.cupon.refresh_from_db()
        self.assertEqual(self.cupon.disponibilidad, 4)  # 5 - 1

        # Verificar creación del gestor de cupones
        gestor_cupon = GestorCupon.objects.get(usuario=self.usuario, cupon=self.cupon)
        self.assertEqual(gestor_cupon.nombre_cupon, f'Cupon de {self.cupon.local} - {self.cupon.costo_puntos} puntos')
        self.assertIsNotNone(gestor_cupon.url_qr)
        self.assertIsNotNone(gestor_cupon.fecha_canje)


# Macri
class UltimasNotificacionesTests(TestCase):
    def setUp(self):
        # Configuración inicial para las pruebas
        self.client = Client()

        # Crear un usuario
        self.usuario = Usuario.objects.create(
            id=1, 
            email='test@test.com', 
            nombre='Test User', 
            puntaje_acumulado=100
        )

        # Crear notificaciones para el usuario
        Notificacion.objects.create(
            usuario=self.usuario, mensaje="Notificación 1", leido=False, fecha_creacion=now()
        )
        Notificacion.objects.create(
            usuario=self.usuario, mensaje="Notificación 2", leido=True, fecha_creacion=now()
        )
        Notificacion.objects.create(
            usuario=self.usuario, mensaje="Notificación 3", leido=False, fecha_creacion=now()
        )
        Notificacion.objects.create(
            usuario=self.usuario, mensaje="Notificación 4", leido=True, fecha_creacion=now()
        )
        Notificacion.objects.create(
            usuario=self.usuario, mensaje="Notificación 5", leido=False, fecha_creacion=now()
        )

        self.url = reverse('ultimas_notificaciones') 

    def test_usuario_valido_con_notificaciones(self):
        response = self.client.post(
            self.url,
            {'usuario_id': self.usuario.id},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        self.assertEqual(response_data['status'], 'success')
        self.assertIn('notificaciones', response_data)
        self.assertEqual(len(response_data['notificaciones']), 4)  # Máximo 4 notificaciones

    def test_usuario_no_encontrado(self):
        """Caso: Usuario no encontrado."""
        response = self.client.post(
            self.url,
            {'usuario_id': 999},  # Usuario inexistente
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        response_data = response.json()

        self.assertEqual(response_data['error'], 'Usuario no encontrado')

    def test_metodo_no_permitido(self):
        """Caso: Método GET no permitido."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        response_data = response.json()

        self.assertEqual(response_data['error'], 'Método no permitido')

    def test_usuario_valido_sin_notificaciones(self):
        """Caso: Usuario válido sin notificaciones."""
        # Crear un usuario sin notificaciones
        usuario_sin_notificaciones = Usuario.objects.create(
            id=2, 
            email='empty@test.com', 
            nombre='No Notificaciones'
        )

        response = self.client.post(
            self.url,
            {'usuario_id': usuario_sin_notificaciones.id},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        # Verificar que no haya notificaciones
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(len(response_data['notificaciones']), 0)  # Sin notificaciones
        self.assertEqual(response_data['no_leidas'], 0)  # Sin no leídas