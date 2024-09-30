from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Usuario, Cliente  # Asegúrate de importar tu modelo Usuario
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
                "contrasena": user.contrasena,
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


@csrf_exempt
def registrar_usuario(request):
    if request.method == 'POST':
        try:
            datos = json.loads(request.body.decode('utf-8'))
            print(f"Datos recibidos: {datos}")  # Debugging

            # Extraer datos directamente sin anidación
            cliente_data = {
                'nombre': datos.get('nombre'),
                'apellido': datos.get('apellido'),
                'direccion': datos.get('direccion'),
                'numero_contacto': datos.get('numero_contacto'),
                'DNI': datos.get('DNI'),
                'genero': datos.get('genero')
            }
            email = datos.get('email')
            contrasena = datos.get('contrasena')

            # Validaciones
            if not email or not contrasena:
                return JsonResponse({'error': 'Email y contraseña son obligatorios'}, status=400)

            # Validar que el cliente tenga los campos necesarios
            required_cliente_fields = ['nombre', 'apellido', 'direccion', 'numero_contacto', 'DNI', 'genero']
            for field in required_cliente_fields:
                if not cliente_data.get(field):
                    print(f"Falta el campo: {field}")  # Debugging
                    return JsonResponse({'error': f'El campo {field} es obligatorio para el cliente'}, status=400)

            # Crear el cliente
            cliente = Cliente(
                nombre=cliente_data.get('nombre'),
                apellido=cliente_data.get('apellido'),
                direccion=cliente_data.get('direccion'),
                numero_contacto=cliente_data.get('numero_contacto'),
                DNI=cliente_data.get('DNI'),
                genero=cliente_data.get('genero')
            )

            # Validar la información del cliente
            cliente.verificar_informacion()

            # Guardar el cliente en la base de datos
            cliente.save()

            # Crear el usuario asociado
            usuario = Usuario(
                email=email,
                contrasena=contrasena,
                cliente=cliente
            )
            usuario.set_contrasena(contrasena)

            # Guardar el usuario en la base de datos
            usuario.save()

            return JsonResponse({'mensaje': 'Usuario registrado exitosamente'}, status=201)

        except ValueError as e:
            print(f"Error de valor: {str(e)}")  # Debugging
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            print(f"Error: {str(e)}")  # Debugging
            return JsonResponse({'error': 'Error interno del servidor: ' + str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)