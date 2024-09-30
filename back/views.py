from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Usuario  # Asegúrate de importar tu modelo Usuario
import json

@csrf_exempt  # Desactiva la protección CSRF para este endpoint
def prueba(request):
    if request.method == 'POST':
        # Obtener los datos del request
        data = json.loads(request.body)
        email = data.get('email')
        contrasena = data.get('contrasena')

        try:
            # Buscar el usuario en la base de datos por correo electrónico
            user = Usuario.objects.get(email=email)

            # Validar la contraseña
            if user.verificar_contrasena(contrasena):
                # Devuelve la información del usuario si las credenciales son correctas
                user_data = {
                    "id": user.id,
                    "email": user.email,
                    "nombres": user.cliente.nombre,
                    "apellidos": user.cliente.apellido,
                    "DNI": user.cliente.DNI,
                    "direccion": user.cliente.direccion,
                    "genero": user.cliente.genero,
                    "puntaje_acumulado": user.puntaje_acumulado,
                    "cantidad_residuos_acumulados": user.cantidad_residuos_acumulados,
                }
                return JsonResponse(user_data)

        except Usuario.DoesNotExist:
            return JsonResponse({'message': 'Credenciales incorrectas'}, status=400)  # Usuario no encontrado

        return JsonResponse({'message': 'Credenciales incorrectas'}, status=400)  # Contraseña incorrecta

    return JsonResponse({'message': 'Método no permitido'}, status=405)  # Mensaje para métodos no permitidos
