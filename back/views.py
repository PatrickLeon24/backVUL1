from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services.usuario_service import UsuarioService, UsuarioAdminService, UsuarioServiceFactory
from .services.plan_service import PlanService
from .services.cupones_o import CuponesO
from .services.pago_service import PagoService
from .services.gestor_plan_service import GestorPlanService
from .models import*
import json
from django.utils import timezone  # Para manejar la fecha de hoy

@csrf_exempt
def inicio_sesion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        contrasena = data.get('contrasena')

        user = Usuario.objects.filter(email=email).first()
        
        if not user:
            return JsonResponse({'message': 'Usuario no encontrado'}, status=400)

        tipo_usuario = user.tipousuario.tipo

        try:
            usuario_service = UsuarioServiceFactory.get_usuario_service(tipo_usuario)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

        user = usuario_service.verificar_credenciales(email, contrasena)
        if user:
            return JsonResponse(usuario_service.obtener_datos_usuario(user))

        return JsonResponse({'message': 'Credenciales incorrectas'}, status=400)

    return JsonResponse({'message': 'Método no permitido'}, status=405)

@csrf_exempt
def registrar_usuario(request):
    if request.method == 'POST':
        # Mostrar los datos recibidos para depurar
        print(request.body.decode('utf-8'))  # Ver el cuerpo de la solicitud
        datos = json.loads(request.body.decode('utf-8'))

        # Verificar el tipo de usuario
        tipo_usuario = Tipo_Usuario.objects.filter(id=datos.get('tipo_usuario')).first()
        if not tipo_usuario:
            return JsonResponse({'error': 'Tipo de usuario no válido'}, status=400)

        # Verificar la contraseña
        if not UsuarioService.verificar_contrasena(datos.get('contrasena')):
            return JsonResponse({'error': 'La contraseña debe tener 8 caracteres como mínimo'}, status=400)

        # Crear el usuario
        UsuarioService.crear_usuario(datos, tipo_usuario)
        return JsonResponse({'mensaje': 'Usuario registrado exitosamente'}, status=201)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_tipos_usuario(request):
    if request.method == 'GET':
        tipos_usuario = Tipo_Usuario.objects.all().values('id', 'tipo')
        return JsonResponse(list(tipos_usuario), safe=False)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_planes_recojo(request):
    if request.method == 'GET':
        planes_data = PlanService.obtener_planes()
        return JsonResponse(planes_data, safe=False)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_plan_usuario(request, usuario_id):
    if request.method == 'GET':
        plan_data = PlanService.obtener_plan_contratado(usuario_id)
        if "error" in plan_data:
            return JsonResponse(plan_data, status=404)
        return JsonResponse(plan_data, safe=False)
    else:
        return JsonResponse({'error': 'Método no permitido.'}, status=405)

@csrf_exempt
def obtener_cupons(request):
    if request.method == 'GET':
        cuponesData = CuponesO.ObtenerCupones()
        return JsonResponse(cuponesData, safe=False)
    
    return JsonResponse({'error': 'Método no permitido.'}, status=405)

@csrf_exempt
def guardar_cambio_contrasena(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        contrasena_actual = data.get('contrasena_actual')
        nueva_contrasena = data.get('nueva_contrasena')
        print(email)
        print(contrasena_actual)
        print(nueva_contrasena)
        # Validar que el usuario existe
        usuario = UsuarioService.verificar_credenciales(email,contrasena_actual)
        if not usuario:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        # Validar la nueva contraseña
        if not UsuarioService.verificar_contrasena(nueva_contrasena):
            return JsonResponse({'error': 'La nueva contraseña no cumple con los requisitos mínimos'}, status=400)
        
        # Verificar la contraseña actual
        # Cambiar la contraseña
        try:
            UsuarioService.cambiar_contrasena(email, contrasena_actual, nueva_contrasena)
            return JsonResponse({'mensaje': 'Contraseña cambiada exitosamente'}, status=200)
        except Exception as e:
            return JsonResponse({'error': 'Error al cambiar la contraseña'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def crear_pago(request):
    if request.method == 'POST':
        # Obtener los datos de la solicitud
        data = json.loads(request.body)
        estado = data.get('estado')
        metodo_pago = data.get('metodo_pago')
        fecha_pago = data.get('fecha_pago')

        # Validar que los campos no estén vacíos
        if not estado or not metodo_pago or not fecha_pago:
            return JsonResponse({'error': 'Faltan campos obligatorios'}, status=400)

        # Crear el pago utilizando el servicio
        try:
            nuevo_pago = PagoService.crear_pago(estado, metodo_pago, fecha_pago)
            return JsonResponse({
                'mensaje': 'Pago creado exitosamente',
                'pago_id': nuevo_pago.id
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def guardar_perfil(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('id')

            # Verifica que el usuario existe
            usuario = Usuario.objects.filter(id=user_id).first()
            if not usuario:
                return JsonResponse({'error': 'Usuario no encontrado.'}, status=404)

            # Actualiza los campos con los nuevos datos
            usuario.nombre = data.get('nombres', usuario.nombre)
            usuario.apellido = data.get('apellidos', usuario.apellido)
            usuario.DNI = data.get('DNI', usuario.DNI)
            usuario.direccion = data.get('direccion', usuario.direccion)
            usuario.numero_contacto = data.get('numero_contacto', usuario.numero_contacto)
            usuario.email = data.get('email', usuario.email)

            # Guarda los cambios
            usuario.save()

            return JsonResponse({'mensaje': 'Perfil actualizado correctamente.'}, status=200)
        
        except Exception as e:
            return JsonResponse({'error': f'Error al procesar la solicitud: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido.'}, status=405)

@csrf_exempt
def crear_gestor_plan(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        usuario_id = data.get('usuario_id')
        plan_id = data.get('plan_id')
        pago_id = data.get('pago_id')

        print(usuario_id, plan_id, pago_id)
        # Verificar que los campos no estén vacíos
        if not usuario_id or not plan_id or not pago_id:
            return JsonResponse({'error': 'Faltan campos obligatorios'}, status=400)

        try:
            # Llamar al servicio para crear el GestorPlan
            gestor_plan = GestorPlanService.crear_gestor_plan(usuario_id, plan_id, pago_id)
            return JsonResponse({
                'mensaje': 'GestorPlan creado exitosamente',
                'gestor_plan_id': gestor_plan.id
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def iniciar_recojo(request):
    if request.method == 'POST':
        try:
            # Obtener datos del cuerpo de la solicitud
            data = json.loads(request.body)
            usuario_id = data.get('usuario_id')

            # Validar que se haya enviado el usuario_id
            if not usuario_id:
                return JsonResponse({'error': 'Faltan campos obligatorios: usuario_id'}, status=400)

            # Verificar que el usuario exista
            usuario = Usuario.objects.filter(id=usuario_id).first()
            if not usuario:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

            # Obtener el gestor de plan del usuario
            gestor_plan = GestorPlan.objects.filter(usuario=usuario).first()
            if not gestor_plan:
                return JsonResponse({'error': 'No se encontró un plan asociado para el usuario'}, status=404)

            # Crear una nueva trayectoria con estado "1" y la fecha de hoy
            nueva_trayectoria = Trayectoria.objects.create(estado="1", fecha_fin=None)
            
            # Crear un nuevo recojo con la fecha de hoy y asociarlo al plan y trayectoria
            nuevo_recojo = Recojo.objects.create(
                fecha_ingreso=timezone.now().date(),
                activo=True,
                plan=gestor_plan.plan,
                trayectoria=nueva_trayectoria
            )

            return JsonResponse({
                'mensaje': 'Recojo iniciado exitosamente',
                'recojo_id': nuevo_recojo.id,
                'trayectoria_id': nueva_trayectoria.id
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': f'Error al iniciar el recojo: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def verificar_trayectoria_recojo(request):
    if request.method == 'POST':
        try:
            # Obtener datos del cuerpo de la solicitud
            data = json.loads(request.body)
            usuario_id = data.get('usuario_id')

            # Validar que se haya enviado el usuario_id
            if not usuario_id:
                return JsonResponse({'error': 'Faltan campos obligatorios: usuario_id'}, status=400)

            # Verificar que el usuario exista
            usuario = Usuario.objects.filter(id=usuario_id).first()
            if not usuario:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

            # Obtener el gestor de plan del usuario
            gestor_plan = GestorPlan.objects.filter(usuario=usuario).first()
            if not gestor_plan:
                return JsonResponse({'error': 'No se encontró un plan asociado para el usuario'}, status=404)

            # Obtener el recojo más reciente del plan del usuario
            recojo = Recojo.objects.filter(plan=gestor_plan.plan, activo=True).order_by('-fecha_ingreso').first()
            print(recojo.fecha_ingreso)
            if not recojo:
                return JsonResponse({'error': 'No se encontró un recojo activo para el usuario'}, status=404)

            # Verificar el estado de la trayectoria del recojo
            trayectoria = recojo.trayectoria
            print(trayectoria.estado)
            return JsonResponse({'estado_trayectoria': 4, 'mensaje': f'El recojo está en la trayectoria {trayectoria.estado}'}, status=200)

        except Exception as e:
            return JsonResponse({'error': f'Error al verificar la trayectoria del recojo: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_recojos(request):
    if request.method == 'GET':
        try:
            usuarios_con_recojos = UsuarioAdminService.obtener_usuarios_con_recojos()
            # Extraer campos relevantes
            usuarios_data = usuarios_con_recojos.values(
                'id', 'nombre', 'apellido',
                'gestorplan__plan__nombre',
                'gestorplan__recojo__fecha_ingreso'
            )
            return JsonResponse(list(usuarios_data), safe=False, status=200)
        except Exception as e:
            # Devuelve el error en un formato JSON
            return JsonResponse({'error': f'Error al obtener los usuarios con recojo: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)