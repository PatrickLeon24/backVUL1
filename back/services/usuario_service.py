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
    def obtener_usuario_por_email(email):
        return Usuario.objects.filter(email=email).first()
    
   
    
    
    @staticmethod
    def cambiar_contrasena(email,contrasena, nueva_contrasena):
        user = Usuario.objects.filter(email=email, contrasena=contrasena).first()
        if user:
            user.contrasena=nueva_contrasena
            user.save()
        
        
    @staticmethod
    def obtener_datos_usuario(user):
        return {
            "id": user.id,
            "email": user.email,
            "contrasena": user.contrasena,
            "nombres": user.nombre,
            "apellidos": user.apellido,
            "numero_contacto": user.numero_contacto,
            "DNI": user.DNI,
            "direccion": user.direccion,
            "genero": user.genero,
            "puntaje_acumulado": user.puntaje_acumulado,
            "cantidad_residuos_acumulados": user.cantidad_residuos_acumulados,
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
            # Aquí podrías hacer cualquier validación que necesites
            usuario.save()
            return usuario
        except Exception as e:
            print(f"Error al crear el usuario: {str(e)}")  # Añadir print para depuración
            raise  # Vuelve a lanzar la excepción

class UsuarioAdminService(UsuarioService):
    @staticmethod
    def verificar_credenciales(email, contrasena):
        user = Usuario.objects.filter(email=email, tipousuario__tipo='admin').first()
        if user and UsuarioService.verificar_contrasena(contrasena):
            return user
        return None