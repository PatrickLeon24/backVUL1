from back.models import Usuario, CodigoInvitacion, Token, Recojo_trayectoria, Recojo
from django.utils import timezone
import random
import string
from back.services.recojo_trayectoria_service import RecojoTrayectoriaService
from back.services.recojo_service import RecojoService
from back.services.pago_service import PagoService

class UsuarioService:
    @staticmethod
    def verificar_contrasena(contrasena):
        if len(contrasena) < 8:
            return False
        return True

    @staticmethod
    def cambiar_contrasena(email, contrasena, nueva_contrasena):
        user = Usuario.objects.filter(email=email, contrasena=contrasena).first()
        if user:
            user.contrasena = nueva_contrasena
            user.save()

    @staticmethod
    def actualizar_perfil(email, nuevos_datos):
        usuario = Usuario.objects.filter(email=email).first()
        if usuario:
            for campo, valor in nuevos_datos.items():
                if valor:
                    setattr(usuario, campo, valor)
            usuario.save()
            return usuario
        return None

    @staticmethod
    def crear_usuario(datos, tipo_usuario):
        usuario = Usuario(
            email=datos.get('email'),
            contrasena=datos.get('contrasena'),
            nombre=datos.get('nombre'),
            apellido=datos.get('apellido'),
            direccion=datos.get('direccion'),
            numero_contacto=datos.get('numero_contacto'),
            DNI=datos.get('DNI'),
            genero=datos.get('genero'),
            puntaje_acumulado=0,
            tipousuario=tipo_usuario
        )
        usuario.save()
        return usuario

    @staticmethod
    def cambiar_contrasena_con_token(email, token_recibido, nueva_contrasena):
        usuario = Usuario.objects.filter(email=email).first()
        
        if not usuario:
            return {'error': 'Usuario no encontrado.'}

        # Verifica el token
        token = Token.objects.filter(usuario=usuario, token=token_recibido, activo=True).first()
        if not token:
            return {'error': 'Token no válido o caducado.'}

        # Verifica que la nueva contraseña cumpla los requisitos
        if not UsuarioService.verificar_contrasena(nueva_contrasena):
            return {'error': 'La contraseña nueva no cumple los requisitos de seguridad.'}

        # Cambia la contraseña del usuario
        usuario.contrasena = nueva_contrasena
        usuario.save()

        # Desactiva el token después de usarlo
        token.activo = False
        token.save()

        return {'message': 'Contraseña cambiada exitosamente.'}

class UsuarioAdminService(UsuarioService):
    @staticmethod
    def verificar_credenciales(email, contrasena):
        user = Usuario.objects.filter(email=email, tipousuario__tipo='Administrador', contrasena=contrasena).first()
        if user:
            return user
        return None

    @staticmethod
    def obtener_datos_usuario(user):
        return {
            "usuario_id": user.id,
            "email": user.email,
            "nombres": user.nombre,
            "apellidos": user.apellido,
            "numero_contacto": user.numero_contacto,
            "DNI": user.DNI,
            "direccion": user.direccion,
            "genero": user.genero,
            "tipousuario": user.tipousuario.tipo
        }
    
    @staticmethod
    def obtener_usuarios_con_recojos():
        # Obtiene todos los usuarios que tienen un recojo activo
        usuarios_con_recojos = Usuario.objects.filter(gestorplan__recojo__activo=True)
        return usuarios_con_recojos

    @staticmethod
    def generar_codigo_invitacion(usuario_admin):
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))  # Genera un código aleatorio
        nuevo_codigo = CodigoInvitacion(codigo=codigo, creado_por=usuario_admin)
        nuevo_codigo.save()
        return nuevo_codigo.codigo
    
    @staticmethod
    def obtener_usuarios_valido(user_id):
    # Obtiene todos los usuarios que tienen un recojo activo filtrando por user_id
        usuarios_con_recojos = Usuario.objects.filter(
            id=user_id,
            
        )
        return usuarios_con_recojos

    @staticmethod
    def siguiente_trayectoria(recojo, administrador, usuario, nueva_trayectoria_id, estado_mensaje):
        return RecojoTrayectoriaService.siguiente(recojo, administrador, usuario, nueva_trayectoria_id, estado_mensaje)

    @staticmethod
    def retroceder_trayectoria(recojo, administrador, usuario):
        return RecojoTrayectoriaService.retroceder(recojo, administrador, usuario)
    
    @staticmethod
    def finalizar_recojo(recojo, administrador, usuario, gestor_plan):
        return RecojoService.finalizar(recojo, administrador, usuario, gestor_plan)
    
    @staticmethod
    def validacion_pago(pago_id):
        return PagoService.validar_pago(pago_id)

class UsuarioClienteService(UsuarioService):

    @staticmethod
    def verificar_credenciales(email, contrasena):
        user = Usuario.objects.filter(email=email, contrasena=contrasena).first()
        if user:
            return user
        return None
    
    @staticmethod
    def obtener_datos_usuario(user):
        return {
            "usuario_id": user.id,
            "email": user.email,
            "nombres": user.nombre,
            "apellidos": user.apellido,
            "numero_contacto": user.numero_contacto,
            "DNI": user.DNI,
            "direccion": user.direccion,
            "genero": user.genero,
            "puntaje_acumulado": user.puntaje_acumulado,
            "tipousuario": user.tipousuario.tipo
        }

    @staticmethod
    def obtener_usuarios_con_recojosus(user_id):
    # Obtiene todos los usuarios que tienen un recojo activo filtrando por user_id
        usuarios_con_recojos = Usuario.objects.filter(
            id=user_id,
            gestorplan__recojo__activo=False,
            gestorplan__recojo__recojo_trayectoria__trayectoria__estado =4
            
            
        )
        return usuarios_con_recojos
    
    @staticmethod
    def cancelar_recojo(usuario_id):
        if not usuario_id:
            return {'error': 'Faltan campos obligatorios: usuario_id', 'status': 400}

        # Verificar que el usuario exista
        usuario = Usuario.objects.filter(id=usuario_id).first()
        if not usuario:
            return {'error': 'Usuario no encontrado', 'status': 404}

        # Verificar si hay un recojo activo para el usuario
        recojo_activo = Recojo.objects.filter(gestor_plan__usuario=usuario, activo=True).first()
        if not recojo_activo:
            return {'error': 'No hay recojos activos para cancelar.', 'status': 400}

        # Obtener la última trayectoria asociada al recojo
        ultima_trayectoria = Recojo_trayectoria.objects.filter(recojo=recojo_activo).order_by('id').last()

        # Verificar que la última trayectoria tenga estado "1"
        if ultima_trayectoria.trayectoria.estado != '1':
            return {'error': 'El recojo no se puede cancelar porque ya se superó el primer estado.', 'status': 400}

        # Actualizar el estado del recojo a inactivo
        recojo_activo.activo = False
        recojo_activo.save()

        # Devolver el recojo cancelado al gestor de planes
        gestor_plan = recojo_activo.gestor_plan
        if gestor_plan:
            gestor_plan.recojos_solicitados -= 1
            gestor_plan.save()

        return {
            'mensaje': 'Recojo cancelado y devuelto exitosamente al gestor de planes',
            'recojo_id': recojo_activo.id,
            'recojos_solicitados': gestor_plan.recojos_solicitados,
            'status': 200
        }
    
class UsuarioServiceFactory:
    @staticmethod
    def get_usuario_service(tipo_usuario):
        if tipo_usuario == 'Administrador':
            return UsuarioAdminService()
        elif tipo_usuario == 'Cliente':
            return UsuarioClienteService()
        else:
            raise ValueError(f"Tipo de usuario desconocido: {tipo_usuario}")