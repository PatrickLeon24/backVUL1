from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Usuario  # Asegúrate de importar tu modelo Usuario
import json

@csrf_exempt
def prueba(request):
    if request.method == 'POST':
        print("Request Body:", request.body)  # Imprimir el cuerpo de la solicitud
        data = json.loads(request.body)
        email = data.get('email')
        contrasena = data.get('contrasena')

        user = Usuario.objects.filter(email=email).first()  # Busca el usuario

        if user and user.verificar_contrasena(contrasena):  # Verifica la contraseña
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
            return JsonResponse(user_data)  # Retorna datos del usuario si es correcto

        return JsonResponse({'message': 'Credenciales incorrectas'}, status=400)

    return JsonResponse({'message': 'Método no permitido'}, status=405)
