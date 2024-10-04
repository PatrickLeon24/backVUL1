from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import*
import json

@csrf_exempt
def inicio_sesion(request):
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
                "nombres": user.nombre,
                "apellidos": user.apellido,
                "DNI": user.DNI,
                "direccion": user.direccion,
                "genero": user.genero,
                "puntaje_acumulado": user.puntaje_acumulado,
                "cantidad_residuos_acumulados": user.cantidad_residuos_acumulados,
            }
            return JsonResponse(user_data)  # Retorna datos del usuario si es correcto

        return JsonResponse({'message': 'Credenciales incorrectas'}, status=400)

    return JsonResponse({'message': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_tipos_usuario(request):
    if request.method == 'GET':
        tipos_usuario = Tipo_Usuario.objects.all().values('id', 'tipo')
        return JsonResponse(list(tipos_usuario), safe=False)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def registrar_usuario(request):
    if request.method == 'POST':
        try:
            datos = json.loads(request.body.decode('utf-8'))
            print(f"Datos recibidos: {datos}")  # Debugging

            # Extraer datos directamente
            usuario_data = {
                'nombre': datos.get('nombre'),
                'apellido': datos.get('apellido'),
                'direccion': datos.get('direccion'),
                'numero_contacto': datos.get('numero_contacto'),
                'DNI': datos.get('DNI'),
                'genero': datos.get('genero'),
            }
            email = datos.get('email')
            contrasena = datos.get('contrasena')
            tipousuario = datos.get('tipo_usuario') 

            # Validaciones
            if not email or not contrasena:
                return JsonResponse({'error': 'Email y contraseña son obligatorios'}, status=400)

            # Validar que el usuario tenga los campos necesarios
            required_usuario_fields = ['nombre', 'apellido', 'direccion', 'numero_contacto', 'DNI', 'genero']
            for field in required_usuario_fields:
                if not usuario_data.get(field):
                    print(f"Falta el campo: {field}")
                    return JsonResponse({'error': f'El campo {field} es obligatorio para el usuario'}, status=400)
            try:
                tipousuario = Tipo_Usuario.objects.get(id=int(tipousuario))  # Convertir el ID a entero
            except (Tipo_Usuario.DoesNotExist, ValueError):
                return JsonResponse({'error': 'El tipo de usuario no es válido'}, status=400)

            # Crear el usuario
            usuario = Usuario(
                email=email,
                contrasena=contrasena,
                nombre=usuario_data.get('nombre'),
                apellido=usuario_data.get('apellido'),
                direccion=usuario_data.get('direccion'),
                numero_contacto=usuario_data.get('numero_contacto'),
                DNI=usuario_data.get('DNI'),
                genero=usuario_data.get('genero'),
                puntaje_acumulado=0,
                cantidad_residuos_acumulados=0, 
                tipousuario=tipousuario 
            )

            # Validar la información del usuario
            usuario.verificar_informacion()

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

def obtener_planes_recojo(request):
    if request.method == 'GET':
        planes = Plan.objects.all()  # Asegúrate de que la clase sea Plan
        planes_data = []

        for plan in planes:
            plan_data = {
                "id": plan.id,
                "nombre": plan.nombre,
                "descripcion": plan.descripcion,
                "imagen": plan.imagen,
                "precio": plan.precio,
                "aserrin": plan.aserrin,
                "baldes": plan.baldes,
                "duracion": plan.duracion,
                "frecuencia_recojo": plan.frecuencia_recojo,
                "cantidad_compostaje": plan.cantidad_compostaje,
                "puntos_plan": plan.puntos_plan,
            }
            planes_data.append(plan_data)

        return JsonResponse(planes_data, safe=False)  # Retorna la lista de planes en formato JSON

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_plan_contratado(request, usuario_id):
    if request.method == 'GET':
        try:
            # Obtener el servicio activo del usuario
            servicio = Recojo.objects.get(usuario__id=usuario_id, activo=True)  # Asegúrate de que el modelo sea Recojo
            plan = servicio.plan

            # Construir la respuesta
            plan_data = {
                "id": plan.id,
                "nombre": plan.nombre,
                "descripcion": plan.descripcion,
                "imagen": plan.imagen,
                "precio": plan.precio,
                "aserrin": plan.aserrin,
                "baldes": plan.baldes,
                "duracion": plan.duracion,
                "frecuencia_recojo": plan.frecuencia_recojo,
                "cantidad_compostaje": plan.cantidad_compostaje,
                "puntos_plan": plan.puntos_plan,
            }

            return JsonResponse(plan_data, status=200)  # Retorna datos del plan contratado

        except Recojo.DoesNotExist:
            return JsonResponse({'error': 'No se encontró un servicio activo para este usuario.'}, status=404)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def obtener_plan_usuario(request, usuario_id):
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        gestor_plan = GestorPlan.objects.filter(usuario=usuario).first()
        
        if gestor_plan and gestor_plan.plan:
            plan = gestor_plan.plan
            plan_data = {
                "id": plan.id,
                "nombre": plan.nombre,
                "descripcion": plan.descripcion,
                "imagen": plan.imagen,
                "precio": plan.precio,
                "aserrin": plan.aserrin,
                "baldes": plan.baldes,
                "duracion": plan.duracion,
                "frecuencia_recojo": plan.frecuencia_recojo,
                "cantidad_compostaje": plan.cantidad_compostaje,
                "puntos_plan": plan.puntos_plan,
            }
            return JsonResponse(plan_data, safe=False)
        else:
            return JsonResponse({'error': 'El usuario no tiene un plan contratado.'}, status=404)
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado.'}, status=404)