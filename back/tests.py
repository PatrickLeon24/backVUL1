from django.test import TestCase, Client
from django.urls import reverse
from django.http import JsonResponse
from back.models import Tipo_Usuario, CodigoInvitacion, Usuario
from unittest.mock import patch

class RegistrarUsuarioTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('registrar_usuario')

        # Crear tipos de usuario
        self.tipo_usuario_normal = Tipo_Usuario.objects.create(id=1, tipo="Usuario")
        self.tipo_usuario_admin = Tipo_Usuario.objects.create(id=2, tipo="Administrador")

        # Crear un usuario para asignar al campo `creado_por`
        self.creador = Usuario.objects.create(nombre="pleon", contrasena="securepassword", tipousuario=self.tipo_usuario_admin)

        # Crear un código de invitación válido con un creador
        self.codigo_invitacion = CodigoInvitacion.objects.create(
            codigo="INVI123",
            utilizado=False,
            creado_por=self.creador  # Asignar el usuario creado
        )

    @patch('back.services.usuario_service.UsuarioService.verificar_contrasena', return_value=True)
    @patch('back.services.usuario_service.UsuarioService.crear_usuario')
    def test_usuario_normal_registrado_exitosamente(self, mock_crear_usuario, mock_verificar_contrasena):
        datos = {
            "tipo_usuario": self.tipo_usuario_normal.id,
            "contrasena": "password123",
        }
        response = self.client.post(self.url, data=datos, content_type="application/json")

        self.assertEqual(response.status_code, 201)
        self.assertJSONEqual(response.content, {"mensaje": "Usuario registrado exitosamente"})
        mock_crear_usuario.assert_called_once_with(datos, self.tipo_usuario_normal)

    @patch('back.services.usuario_service.UsuarioService.verificar_contrasena', return_value=False)
    def test_contrasena_invalida(self, mock_verificar_contrasena):
        datos = {
            "tipo_usuario": self.tipo_usuario_normal.id,
            "contrasena": "short",
        }
        response = self.client.post(self.url, data=datos, content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "La contraseña debe tener 8 caracteres como mínimo"})

    def test_tipo_usuario_invalido(self):
        datos = {
            "tipo_usuario": 999,  # ID inexistente
            "contrasena": "password123",
        }
        response = self.client.post(self.url, data=datos, content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Tipo de usuario no válido"})

    def test_codigo_invitacion_faltante_para_administrador(self):
        datos = {
            "tipo_usuario": self.tipo_usuario_admin.id,
            "contrasena": "password123",
        }
        response = self.client.post(self.url, data=datos, content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Se requiere un código de invitación para registrarse como administrador"})

    def test_codigo_invitacion_invalido_o_utilizado(self):
        datos = {
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
