from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services.usuario_service import UsuarioService, UsuarioAdminService, UsuarioServiceFactory
from .services.plan_service import PlanService
from .services.cupones_o import CuponesO
from .services.pago_service import PagoService
from .services.gestor_plan_service import GestorPlanService
from .models import*
import json
from django.utils import timezone

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
        datos = json.loads(request.body)

        # Verificar el tipo de usuario
        tipo_usuario = Tipo_Usuario.objects.filter(id=datos.get('tipo_usuario')).first()
        if not tipo_usuario:
            return JsonResponse({'error': 'Tipo de usuario no válido'}, status=400)

        # Verificar la contraseña
        if not UsuarioService.verificar_contrasena(datos.get('contrasena')):
            return JsonResponse({'error': 'La contraseña debe tener 8 caracteres como mínimo'}, status=400)

        # Validar código de invitación si el usuario es administrador
        if tipo_usuario.tipo == 'Administrador':
            codigo_invitacion = datos.get('codigo_invitacion')
            if not codigo_invitacion:
                return JsonResponse({'error': 'Se requiere un código de invitación para registrarse como administrador'}, status=400)

            # Verificar si el código de invitación es válido
            try:
                codigo = CodigoInvitacion.objects.get(codigo=codigo_invitacion, utilizado=False)
                # Marcar el código como utilizado
                codigo.utilizado = True
                codigo.save()
            except CodigoInvitacion.DoesNotExist:
                return JsonResponse({'error': 'Código de invitación inválido o ya utilizado'}, status=400)

        # Crear el usuario
        UsuarioService.crear_usuario(datos, tipo_usuario)
        return JsonResponse({'mensaje': 'Usuario registrado exitosamente'}, status=201)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt  # Desactiva la verificación CSRF (haz esto solo si es necesario)
def generar_codigo_invitacion(request):
    if request.method == 'POST':
        try:
            # Lee el cuerpo JSON de la solicitud
            data = json.loads(request.body)
            admin_id = data.get('admin_id')

            # Busca al administrador en la base de datos
            usuario_admin = Usuario.objects.get(id=admin_id)  # Asegúrate de que esto esté bien manejado

            # Llama al método estático de tu servicio pasando el usuario_admin
            codigo = UsuarioAdminService.generar_codigo_invitacion(usuario_admin)
            return JsonResponse({'codigo': codigo}, status=200)
        except Usuario.DoesNotExist:
            return JsonResponse({'error': 'Administrador no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

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
        # Obtener los parámetros de filtro desde la URL
        precio_min = request.GET.get('precio_min', None)
        precio_max = request.GET.get('precio_max', None)
        frecuencia_recojo = request.GET.get('frecuencia_recojo', None)

        # Convertir los parámetros numéricos a float si están presentes
        if precio_min is not None:
            precio_min = float(precio_min)
        if precio_max is not None:
            precio_max = float(precio_max)

        # Llamar al servicio con los filtros
        planes_data = PlanService.obtener_planes(
            precio_min=precio_min, 
            precio_max=precio_max, 
            frecuencia_recojo=frecuencia_recojo
        )
        
        return JsonResponse(planes_data, safe=False)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_plan_usuario(request, usuario_id):
    if request.method == 'GET':
        plan_data = GestorPlanService.obtener_plan_contratado(usuario_id)
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
        tipo_usuario = data.get('tipo_usuario')

        # Obtiene el servicio correspondiente según el tipo de usuario
        usuario_service = UsuarioServiceFactory.get_usuario_service(tipo_usuario)

        # Validar que el usuario existe
        usuario = usuario_service.verificar_credenciales(email, contrasena_actual)
        if not usuario:
            return JsonResponse({'error': 'Credenciales inválidas'}, status=404)

        # Validar la nueva contraseña
        if not usuario_service.verificar_contrasena(nueva_contrasena):
            return JsonResponse({'error': 'La nueva contraseña no cumple con los requisitos mínimos'}, status=400)

        # Cambiar la contraseña
        usuario_service.cambiar_contrasena(email, contrasena_actual, nueva_contrasena)
        return JsonResponse({'mensaje': 'Contraseña cambiada exitosamente'}, status=200)

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

            nuevos_datos = {
                'nombre': data.get('nombres'),
                'apellido': data.get('apellidos'),
                'DNI': data.get('DNI'),
                'direccion': data.get('direccion'),
                'numero_contacto': data.get('numero_contacto'),
                'email': data.get('email'),
            }

            # Llama al método actualizar_perfil
            usuario_actualizado = UsuarioService.actualizar_perfil(usuario.email, nuevos_datos)
            if not usuario_actualizado:
                return JsonResponse({'error': 'Error al actualizar el perfil.'}, status=400)

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
            data = json.loads(request.body)
            usuario_id = data.get('usuario_id')
            print(usuario_id)
            # Validar que se haya enviado el usuario_id
            if not usuario_id:
                return JsonResponse({'error': 'Faltan campos obligatorios: usuario_id'}, status=400)

            # Verificar que el usuario exista
            usuario = Usuario.objects.filter(id=usuario_id).first()
            if not usuario:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
            print(usuario)
            # Verificar si ya hay un recojo activo para el usuario
            recojo_activo = Recojo.objects.filter(gestor_plan__usuario=usuario, activo=True).first()
            if recojo_activo:
                return JsonResponse({'error': 'El recojo solicitado anteriormente aún no se ha completado.'}, status=400)
            print(recojo_activo)
            # Obtener el gestor de plan del usuario
            gestor_plan = GestorPlan.objects.filter(usuario=usuario).last()
            if not gestor_plan:
                return JsonResponse({'error': 'No se encontró un plan asociado para el usuario'}, status=404)
            print(gestor_plan)
            # Verificar si se ha alcanzado la frecuencia máxima de recojos
            if gestor_plan.recojos_solicitados >= gestor_plan.plan.frecuencia_recojo:
                return JsonResponse({'error': 'Se ha alcanzado el limite de recojos por su plan contratado'}, status=400)

            # Incrementar el contador de recojos solicitados
            gestor_plan.recojos_solicitados += 1
            gestor_plan.save()

            # Crear una nueva trayectoria con estado "1"
            nueva_trayectoria = Trayectoria.objects.get(id=1) 
            
            # Crear un nuevo recojo asociado al gestor de plan y la trayectoria inicial
            nuevo_recojo = Recojo.objects.create(
                fecha_ingreso=timezone.now().date(),
                activo=True,
                gestor_plan=gestor_plan,
            )

            # Crear la entrada en la tabla Recojo_trayectoria
            Recojo_trayectoria.objects.create(
                estado_ingreso=timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"),
                recojo=nuevo_recojo,
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
            gestor_plan = GestorPlan.objects.filter(usuario=usuario).last()
            if not gestor_plan:
                return JsonResponse({'error': 'No se encontró un plan asociado para el usuario'}, status=404)

            recojo = Recojo.objects.filter(gestor_plan=gestor_plan, activo=True).last()
            if not recojo:
                return JsonResponse({'error': 'No se encontró un recojo activo para el usuario'}, status=404)

            # Obtener todas las trayectorias de recojo
            trayectorias = Recojo_trayectoria.objects.filter(recojo=recojo).order_by('id')
            if not trayectorias:
                return JsonResponse({'error': 'No se encontraron trayectorias asociadas al recojo'}, status=404)

            # Obtener estado, fecha y administrador para cada trayectoria
            estado_trayectoria = []
            fechas_hora = []
            administradores = []
            for r_t in trayectorias:
                estado_trayectoria.append(r_t.trayectoria.estado)
                estado_ingreso_local = timezone.localtime(r_t.estado_ingreso)
                fechas_hora.append(estado_ingreso_local.strftime('%Y-%m-%d %H:%M'))
                
                # Solo agregar el administrador si existe
                if r_t.administrador:  # Verifica si existe administrador
                    administradores.append(f"{r_t.administrador.nombre} {r_t.administrador.apellido}")
                else:
                    administradores.append("Administrador no asignado")  # Si no hay administrador

            return JsonResponse({
                'estado_trayectoria': estado_trayectoria[-1],  # último estado
                'fechas_hora': fechas_hora,  # Lista de fechas completas
                'administradores': administradores  # Lista de administradores por estado
            }, status=200)

        except Exception as e:
            return JsonResponse({'estado_trayectoria': 0, 'mensaje': f'Error al verificar la trayectoria: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_recojos(request):
    if request.method == 'GET':
        try:
            # Extraer campos relevantes
            usuarios_data = list(UsuarioAdminService.obtener_usuarios_con_recojos().values(
                'id', 'nombre', 'apellido', 'direccion', 'numero_contacto', 'DNI',
                'gestorplan__plan__nombre',
                'gestorplan__recojo__id',  # ID del recojo para identificar el último
                'gestorplan__recojo__fecha_ingreso',
                'gestorplan__recojo__recojo_trayectoria__trayectoria__estado',
                'gestorplan__recojo__recojo_trayectoria__id'  # ID de recojo_trayectoria
            ))

            # Diccionario para almacenar el último recojo por usuario
            usuarios_con_ultimo_recojo = {}

            # Iterar por todos los usuarios y recojos
            for usuario in usuarios_data:
                usuario_id = usuario['id']
                recojo_trayectoria_id = usuario['gestorplan__recojo__recojo_trayectoria__id']

                # Si el usuario no está en el diccionario, lo agregamos
                if usuario_id not in usuarios_con_ultimo_recojo:
                    usuarios_con_ultimo_recojo[usuario_id] = usuario
                else:
                    # Si ya existe el usuario, comparamos el id del recojo_trayectoria actual con el almacenado
                    print(recojo_trayectoria_id)
                    print(usuarios_con_ultimo_recojo[usuario_id]['gestorplan__recojo__recojo_trayectoria__id'])
                    if recojo_trayectoria_id > usuarios_con_ultimo_recojo[usuario_id]['gestorplan__recojo__recojo_trayectoria__id']:
                        usuarios_con_ultimo_recojo[usuario_id] = usuario

            # Convertir el diccionario de vuelta a una lista si lo necesitas
            usuarios_final = list(usuarios_con_ultimo_recojo.values())
            
            return JsonResponse(usuarios_final, safe=False, status=200)
        except Exception as e:
            # Devuelve el error en un formato JSON
            return JsonResponse({'error': f'Error al obtener los usuarios con recojo: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_puntaje_usuario(request, usuario_id):
    if request.method == 'GET':
        try:
            # Obtener el usuario a partir del ID proporcionado
            usuario = Usuario.objects.filter(id=usuario_id).first()
            if not usuario:
                return JsonResponse({'error': 'Usuario no encontrado.'}, status=404)
            # Suponiendo que los puntos del usuario están almacenados en el campo 'puntaje_acumulado'
            puntaje = usuario.puntaje_acumulado
            # Retornar el puntaje en formato JSON
            return JsonResponse({'puntos': puntaje}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Error al obtener el puntaje del usuario: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def consultar_recojo(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            recojo_id = body.get('recojo_id')
            admin_id = body.get('admin_id')

            administrador = Usuario.objects.filter(id=admin_id).first()
            if not administrador:
                return JsonResponse({'error': 'Administrador no encontrado'}, status=404)

            usuario = Usuario.objects.filter(id=recojo_id).first()
            if not usuario:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

            gestor_plan = GestorPlan.objects.filter(usuario=usuario).last()
            if not gestor_plan:
                return JsonResponse({'error': 'No se encontró un plan asociado para el usuario'}, status=404)

            recojo = Recojo.objects.filter(gestor_plan=gestor_plan, activo=True).last()
            if not recojo:
                return JsonResponse({'error': 'No se encontró un recojo activo para el usuario'}, status=404)

            r_t = Recojo_trayectoria.objects.filter(recojo=recojo).last()
            if not r_t:
                return JsonResponse({'error': 'No se encontró una trayectoria asociada al recojo'}, status=404)

            trayecto = r_t.trayectoria

            if int(trayecto.estado) == 1:
                trayectoria_obj = Trayectoria.objects.get(id=2)
                R_tN = Recojo_trayectoria.objects.create(
                    estado_ingreso=timezone.localtime(),
                    recojo=recojo,
                    trayectoria=trayectoria_obj
                )
            elif int(trayecto.estado) == 2:
                trayectoria_obj = Trayectoria.objects.get(id=3)
                R_tN = Recojo_trayectoria.objects.create(
                    estado_ingreso=timezone.localtime(),
                    recojo=recojo,
                    trayectoria=trayectoria_obj,
                    administrador=administrador
                )
            elif int(trayecto.estado) == 3:
                trayectoria_obj = Trayectoria.objects.get(id=4)
                R_tN = Recojo_trayectoria.objects.create(
                    estado_ingreso=timezone.localtime(),
                    recojo=recojo,
                    trayectoria=trayectoria_obj,
                    administrador=administrador
                )
            elif int(trayecto.estado) == 4:
                recojo.activo = False
                recojo.fecha_salida = timezone.now()
                recojo.save()

                puntos_plan = gestor_plan.plan.puntos_plan
                usuario.puntaje_acumulado += puntos_plan
                usuario.save()

            return JsonResponse({'status': 'success', 'recojo': "recojo_data"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

