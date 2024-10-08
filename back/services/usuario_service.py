from back.models import Usuario

class UsuarioService:
    @staticmethod
    def verificar_credenciales(email, contrasena):
        user = Usuario.objects.filter(email=email, contrasena=contrasena).first()
        if user:
            return user
        return None

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

    @staticmethod
    def crear_usuario(datos, tipo_usuario):
        try:
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
        except Exception as e:
            print(f"Error al crear el usuario: {str(e)}")
            raise

class UsuarioAdminService(UsuarioService):
    @staticmethod
    def verificar_credenciales(email, contrasena):
        user = Usuario.objects.filter(email=email, tipousuario__tipo='Administrador').first()
        if user and UsuarioService.verificar_contrasena(contrasena):
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
    
    def obtener_usuarios_con_recojos():
        # Obtiene todos los usuarios que tienen un recojo activo
        usuarios_con_recojos = Usuario.objects.filter(gestorplan__recojo__activo=True).distinct()
        return usuarios_con_recojos

class UsuarioServiceFactory:
    @staticmethod
    def get_usuario_service(tipo_usuario):
        if tipo_usuario == 'Administrador':
            return UsuarioAdminService()
        elif tipo_usuario == 'Cliente':
            return UsuarioService()
        else:
            raise ValueError(f"Tipo de usuario desconocido: {tipo_usuario}")