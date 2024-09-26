from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Datos de ejemplo de usuarios
users = [
    {
        "id": 1,
        "email": "123",
        "password": "123",
        "nombres": "Daniel Alonso",
        "apellidos": "Taype Rojas",
        "DNI": "47245671",
        "direccion": "av los nogales",
        "genero": "hombre"
    }
]

@csrf_exempt  # Desactiva la protección CSRF para este endpoint
def prueba(request):
    if request.method == 'POST':
        # Obtener los datos del request
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        user = {
            "id": 1,
            "email": "123",
            "password": "123",
            "nombres": "Daniel Alonso",
            "apellidos": "Taype Rojas",
            "DNI": "47245671",
            "direccion": "av los nogales",
            "genero": "hombre"
        }
    
        # Validar las credenciales
       
        if "123" == email and "123"== password:
            return JsonResponse(user)  # Devuelve la información del usuario si las credenciales son correctas
        
        return JsonResponse({'message': 'Credenciales incorrectas'}, status=400)  # Mensaje de error si las credenciales son incorrectas

    return JsonResponse({'message': 'Método no permitido'}, status=405)  # Mensaje para métodos no permitidos
