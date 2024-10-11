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

            # Validar que se haya enviado el usuario_id
            if not usuario_id:
                return JsonResponse({'error': 'Faltan campos obligatorios: usuario_id'}, status=400)

            # Verificar que el usuario exista
            usuario = Usuario.objects.filter(id=usuario_id).first()
            if not usuario:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

            # Verificar si ya hay un recojo activo para el usuario
            recojo_activo = Recojo.objects.filter(gestor_plan__usuario=usuario, activo=True).first()
            if recojo_activo:
                return JsonResponse({'error': 'El recojo solicitado anteriormente aún no se ha completado.'}, status=400)

            # Obtener el gestor de plan del usuario
            gestor_plan = GestorPlan.objects.filter(usuario=usuario).last()
            if not gestor_plan:
                return JsonResponse({'error': 'No se encontró un plan asociado para el usuario'}, status=404)

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

            # Obtener estado y fecha completa para cada trayectoria
            estado_trayectoria = []
            fechas_hora = []
            for r_t in trayectorias:
                estado_trayectoria.append(r_t.trayectoria.estado)
                estado_ingreso_local = timezone.localtime(r_t.estado_ingreso)
                fechas_hora.append(estado_ingreso_local.strftime('%Y-%m-%d %H:%M'))

            return JsonResponse({
                'estado_trayectoria': estado_trayectoria[-1],  # último estado
                'fechas_hora': fechas_hora,  # Devolver la lista de fecha completa
            }, status=200)

        except Exception as e:
            return JsonResponse({'estado_trayectoria': 0, 'mensaje': 'Error al verificar la trayectoria'}, status=500)

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
            print(recojo_id)

            # Verifica si el recojo con el ID existe
            usuario = Usuario.objects.filter(id=recojo_id).first()
            if not usuario:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

            gestor_plan = GestorPlan.objects.filter(usuario=usuario).last()
            if not gestor_plan:
                return JsonResponse({'error': 'No se encontró un plan asociado para el usuario'}, status=404)
            print(gestor_plan.usuario)

            # Obtener el recojo más reciente y activo del plan del usuario
            recojo = Recojo.objects.filter(gestor_plan=gestor_plan, activo=True).last()
            print(recojo.id)
            if not recojo:
                return JsonResponse({'error': 'No se encontró un recojo activo para el usuario'}, status=404)

            # Obtener la trayectoria del recojo     
            r_t = Recojo_trayectoria.objects.filter(recojo=recojo).last()
            print(r_t)
            if not r_t:
                return JsonResponse({'error': 'No se encontró una trayectoria asociada al recojo'}, status=404)

            trayecto = r_t.trayectoria
            print("11111")
            print(trayecto.estado)

            # Actualizar estado según la trayectoria
            if int(trayecto.estado) == 1:
                trayectoria_obj = Trayectoria.objects.get(id=2) 
                R_tN = Recojo_trayectoria.objects.create(
                    estado_ingreso=timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"),
                    recojo=recojo,
                    trayectoria=trayectoria_obj
                )
                print("Trayectoria actualizada a 2")
            elif int(trayecto.estado) == 2:
                trayectoria_obj = Trayectoria.objects.get(id=3)
                R_tN = Recojo_trayectoria.objects.create(
                    estado_ingreso=timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"),
                    recojo=recojo,
                    trayectoria=trayectoria_obj
                )
                print("Trayectoria actualizada a 3")
            elif int(trayecto.estado) == 3:
                trayectoria_obj = Trayectoria.objects.get(id=4)
                R_tN = Recojo_trayectoria.objects.create(
                    estado_ingreso=timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"),
                    recojo=recojo,
                    trayectoria=trayectoria_obj
                )
                print("Trayectoria actualizada a 4")
            elif int(trayecto.estado) == 4:
                # Desactivar el recojo
                recojo.activo = False
                recojo.fecha_salida = timezone.now().strftime("%Y-%m-%d")
                recojo.save()
                print("Recojo desactivado")

                # Otorgar puntos al usuario
                puntos_plan = gestor_plan.plan.puntos_plan  # Obtener puntos del plan asociado
                usuario.puntaje_acumulado += puntos_plan  # Sumar puntos al usuario
                usuario.save()
                print(f"Puntos otorgados: {puntos_plan}")

            return JsonResponse({'status': 'success', 'recojo': "recojo_data"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
