from back.models import Usuario, CodigoInvitacion
import random
import string
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
            cantidad_residuos_acumulados=0,
            tipousuario=tipo_usuario
        )
        usuario.save()
        return usuario

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
            "cantidad_residuos_acumulados": user.cantidad_residuos_acumulados,
            "tipousuario": user.tipousuario.tipo
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