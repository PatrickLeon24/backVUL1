from time import localtime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services.usuario_service import UsuarioService, UsuarioAdminService, UsuarioServiceFactory, UsuarioClienteService
from .services.plan_service import PlanService
from .services.cupones_o import CuponesO
from .services.pago_service import PagoService
from .services.gestor_plan_service import GestorPlanService
from .services.gestor_cupon_service import GestorCuponService
from .models import*
import json
from django.utils import timezone
from django.core.mail import EmailMessage, send_mail
import random
import string
from django.core.mail import EmailMessage
from reportlab.lib.pagesizes import letter, A5
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib import colors
from django.contrib.auth.models import User
from django.http import JsonResponse
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os
from django.utils.html import strip_tags
from xhtml2pdf import pisa
from datetime import datetime

@csrf_exempt
def inicio_sesion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        contrasena = data.get('contrasena')
        google=data.get('google')

        user = Usuario.objects.filter(email=email).first()

        # Verificar si se intenta iniciar sesión sin contraseña (Google)
        if (not contrasena) and google==1:
            if user:
                tipo_usuario = user.tipousuario.tipo
                usuario_service = UsuarioServiceFactory.get_usuario_service(tipo_usuario)
                print("sigma:")
                # Devolver los datos del usuario en caso de existir
                return JsonResponse(usuario_service.obtener_datos_usuario(user))
            else:
                print("olaaaaa")
                # Usuario no encontrado para el inicio de sesión de Google
                return JsonResponse({'message': 'No hay cuenta asociada a este correo'}, status=400)

        # Verificar inicio de sesión tradicional con contraseña
        if user:
            tipo_usuario = user.tipousuario.tipo
            try:
                usuario_service = UsuarioServiceFactory.get_usuario_service(tipo_usuario)
            except ValueError as e:
                return JsonResponse({'error': str(e)}, status=400)

            user = usuario_service.verificar_credenciales(email, contrasena)
            if user:
                return JsonResponse(usuario_service.obtener_datos_usuario(user))

            return JsonResponse({'message': 'Credenciales incorrectas'}, status=400)

        return JsonResponse({'message': 'Usuario no encontrado'}, status=400)

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
        monto_pago = data.get('monto_pago')

        print(estado, metodo_pago, fecha_pago, monto_pago)
        # Validar que los campos no estén vacíos
        if not estado or not metodo_pago or not fecha_pago or not monto_pago:
            return JsonResponse({'error': 'Faltan campos obligatorios'}, status=400)

        # Crear el pago utilizando el servicio
        try:
            nuevo_pago = PagoService.crear_pago(estado, metodo_pago, fecha_pago, monto_pago)
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

            if not gestor_plan.validado:
                return JsonResponse({'error': ' El plan aún no ha sido validado para iniciar un recojo'}, status=400)
            
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
                fecha_ingreso=timezone.localtime().date(),
                activo=True,
                gestor_plan=gestor_plan,
            )

            # Crear la entrada en la tabla Recojo_trayectoria
            Recojo_trayectoria.objects.create(
                estado_ingreso=timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"),
                recojo=nuevo_recojo,
                trayectoria=nueva_trayectoria
            )

            Notificacion.objects.create(
                usuario = usuario,
                administrador = None,
                mensaje="Su solicitud ha sido recibida"
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
            print("ola1")
            if not usuario:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

            # Obtener el gestor de plan del usuario
            gestor_plan = GestorPlan.objects.filter(usuario=usuario).last()
            print("ola2")
            if not gestor_plan:
                print("ola")
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

            # Cambiar el estado y enviar notificación según el estado actual
            if int(trayecto.estado) == 1:
                trayectoria_obj = Trayectoria.objects.get(id=2)
                Recojo_trayectoria.objects.create(
                    estado_ingreso=timezone.localtime(),
                    recojo=recojo,
                    trayectoria=trayectoria_obj,
                    administrador=administrador
                )
                Notificacion.objects.create(
                    usuario=usuario,
                    administrador=administrador,
                    mensaje="El estado de su pedido ha cambiado a 'En Preparacion'."
                )
            elif int(trayecto.estado) == 2:
                trayectoria_obj = Trayectoria.objects.get(id=3)
                Recojo_trayectoria.objects.create(
                    estado_ingreso=timezone.localtime(),
                    recojo=recojo,
                    trayectoria=trayectoria_obj,
                    administrador=administrador
                )
                Notificacion.objects.create(
                    usuario=usuario,
                    administrador=administrador,
                    mensaje="El estado de su pedido ha cambiado a 'En camino'."
                )
            elif int(trayecto.estado) == 3:
                trayectoria_obj = Trayectoria.objects.get(id=4)
                Recojo_trayectoria.objects.create(
                    estado_ingreso=timezone.localtime(),
                    recojo=recojo,
                    trayectoria=trayectoria_obj,
                    administrador=administrador
                )
                Notificacion.objects.create(
                    usuario=usuario,
                    administrador=administrador,
                    mensaje="El estado de su pedido ha cambiado a 'Entregado'."
                )
            elif int(trayecto.estado) == 4:
                recojo.activo = False
                recojo.fecha_salida = timezone.localtime()
                recojo.save()

                puntos_plan = gestor_plan.plan.puntos_plan
                usuario.puntaje_acumulado += puntos_plan
                usuario.save()

                # Generar el PDF con los datos
                pdf_buffer = generate_pdf(usuario, gestor_plan)

                # Crear el correo
                email = EmailMessage(
                    'Tu Boleta de Recojo',
                    'Adjunto la boleta PDF con el detalle de tu recojo inactivo.',
                    'verdeulima@gmail.com',
                    [usuario.email], 
                )

                # Adjuntar el archivo PDF generado
                email.attach('boleta_recojo_inactivo.pdf', pdf_buffer.read(), 'application/pdf')

                # Enviar el correo
                email.send()

                # Notificación al usuario
                Notificacion.objects.create(
                    usuario=usuario,
                    administrador=administrador,
                    mensaje="Su pedido ha sido completado, y se le han asignado puntos. Adjuntamos la boleta PDF."
                )

            return JsonResponse({'status': 'success', 'recojo': "recojo_data"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
#######sprint2

@csrf_exempt
def consultar_recojoR(request):
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

            # Retroceder el estado si es mayor que 1
            if int(trayecto.estado) > 1:
                estado=int(trayecto.estado)-1
                trayectoria_obj = Trayectoria.objects.get(id=estado)
                R_tN = Recojo_trayectoria.objects.create(
                    estado_ingreso=timezone.localtime(),
                    recojo=recojo,
                    trayectoria=trayectoria_obj,
                    administrador=administrador
                )
                return JsonResponse({'status': 'success', 'message': 'Estado retrocedido correctamente.'}, status=200)
            else:
                return JsonResponse({'error': 'El estado no puede retroceder más.'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@csrf_exempt
def send_email(request):
    if request.method == 'GET':
        # Datos estáticos
        subject = 'Prueba de lelele'
        message = 'Este es un mensaje de prueba.'
        recipient = '20214404@aloe.ulima.edu.pe'  # Reemplaza con el email fijo que deseas usar

        try:
            send_mail(
                subject,
                message,
                'verdeulima@gmail.com',     # Remitente (debe coincidir con EMAIL_HOST_USER)
                [recipient],              # Lista de destinatarios
                fail_silently=False,
            )
            return JsonResponse({'message': 'Correo enviado exitosamente.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def generar_token(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@csrf_exempt
def enviar_token(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('correo')
        
        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado.'}, status=404)

        token = generar_token()
        nuevo_token = Token(usuario=usuario, token=token, activo=True)
        nuevo_token.save()

        # Enviar el correo
        send_mail(
            'Solicitud de recuperación de contraseña',
            f'Su token de recuperación es: {token}',
            'verdeulima@gmail.com',  # Cambia esto por tu dirección de correo
            [usuario.email],
            fail_silently=False,
        )
        
        return JsonResponse({'message': 'Token enviado al correo del usuario.'}, status=200)
    
@csrf_exempt
def cambiar_contrasena(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('correo')
        token_recibido = data.get('token')
        nueva_contrasena = data.get('nueva_contrasena')

        # Utilizar el método en UsuarioService para cambiar la contraseña
        resultado = UsuarioService.cambiar_contrasena_con_token(email, token_recibido, nueva_contrasena)

        # Verificar el resultado y devolver la respuesta adecuada
        if 'error' in resultado:
            return JsonResponse({'error': resultado['error']}, status=400)
        
        return JsonResponse({'message': resultado['message']}, status=200)

@csrf_exempt
def canjear_cupon(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        usuario_id = data.get('usuario_id')
        cupon_id = data.get('cupon_id')
        
        # Llamar al método de servicio para canjear el cupón
        resultado = GestorCuponService.canjear_cupon(usuario_id, cupon_id)

        # Responder según el resultado
        if 'error' in resultado:
            return JsonResponse({'error': resultado['error']}, status=400 if resultado['error'] != 'Cupón no encontrado' else 404)
        return JsonResponse({'mensaje': resultado['mensaje'], 'url_qr': resultado['url_qr']}, status=200)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_recojos_por_administrador(request, usuario_id):
    if request.method == 'GET':
        try:
            # Filtrar recojos finalizados relacionados con el administrador específico
            recojos_finalizados = Recojo_trayectoria.objects.filter(
                administrador_id=usuario_id,
                trayectoria__estado='4'
            ).values(
                'recojo__fecha_salida',
                'recojo__gestor_plan__usuario__nombre', 
                'recojo__gestor_plan__usuario__apellido', 
                'recojo__gestor_plan__plan__nombre'
            )

            recojos_list = list(recojos_finalizados)
            print(recojos_list)

            return JsonResponse(recojos_list, safe=False, status=200)

        except Exception as e:
            # Manejo de errores
            return JsonResponse({'error': f'Error al obtener los recojos: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def generar_codigo_invitacion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            admin_id = data.get('admin_id')
      
            usuario_admin = Usuario.objects.get(id=admin_id) 
            
            codigo = UsuarioAdminService.generar_codigo_invitacion(usuario_admin)
            return JsonResponse({'codigo': codigo}, status=200)
        except Usuario.DoesNotExist:
            return JsonResponse({'error': 'Administrador no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_codigos_invitacion(request, usuario_id):
    if request.method == 'GET':
        try:
            # Verificar si el administrador existe
            usuario_admin = Usuario.objects.get(id=usuario_id)

            # Filtrar los códigos de invitación generados por este administrador
            codigos_invitacion = CodigoInvitacion.objects.filter(creado_por=usuario_admin)

            # Crear la respuesta JSON manualmente
            codigos_data = [
                {
                    'codigo': codigo.codigo,
                    'utilizado': codigo.utilizado,
                    'fecha_creacion': codigo.fecha_creacion.strftime('%Y-%m-%d') 
                } for codigo in codigos_invitacion
            ]

            return JsonResponse(codigos_data, safe=False, status=200)

        except Usuario.DoesNotExist:
            return JsonResponse({'error': 'Administrador no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def cancelar_recojo(request):
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

            # Verificar si hay un recojo activo para el usuario
            recojo_activo = Recojo.objects.filter(gestor_plan__usuario=usuario, activo=True).first()
            if not recojo_activo:
                return JsonResponse({'error': 'No hay recojos activos para cancelar.'}, status=400)

            # Obtener la última trayectoria asociada al recojo
            ultima_trayectoria = Recojo_trayectoria.objects.filter(recojo=recojo_activo).order_by('id').last()

            # Verificar que la última trayectoria tenga estado "1"
            if ultima_trayectoria.trayectoria.estado != '1':
                return JsonResponse({'error': 'El recojo no se puede cancelar porque ya se superó el primer estado.'}, status=400)

            # Actualizar el estado del recojo a inactivo
            recojo_activo.activo = False
            recojo_activo.save()

            # Devolver el recojo cancelado al gestor de planes
            gestor_plan = recojo_activo.gestor_plan
            if gestor_plan:
                gestor_plan.recojos_solicitados -= 1
                gestor_plan.save()

            return JsonResponse({
                'mensaje': 'Recojo cancelado y devuelto exitosamente al gestor de planes',
                'recojo_id': recojo_activo.id,
                'recojos_solicitados': gestor_plan.recojos_solicitados
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': f'Error al cancelar el recojo: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_recojosus(request, usuario_id):
    if request.method == 'GET':
        user_id = usuario_id

        try:
            # Filtrar por usuario específico y recojos activos
            usuarios_data = list(UsuarioClienteService.obtener_usuarios_con_recojosus(user_id).values(
                'id', 'nombre', 'apellido', 'direccion', 'numero_contacto', 'DNI',
                'gestorplan__plan__nombre',
                'gestorplan__recojo__id',
                'gestorplan__recojo__fecha_ingreso',
                'gestorplan__recojo__fecha_salida',
                'gestorplan__recojo__recojo_trayectoria__trayectoria__estado',
                'gestorplan__recojo__recojo_trayectoria__id'
            ))

            # Diccionario para almacenar el último recojo por usuario
            return JsonResponse(usuarios_data, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Error al obtener los usuarios con recojo: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def obtener_historial_cupones(request, usuario_id):
    try:
        # Obtiene los cupones canjeados por el usuario dado
        cupones_canjeados = GestorCupon.objects.filter(usuario_id=usuario_id)

        # Construye una lista de los cupones canjeados con los datos necesarios
        historial = [
            {
                'nombre_cupon': str(cupon.cupon),  # Usamos el método __str__ para el "nombre"
                'fecha_canje': cupon.fecha_canje,
                'url_qr': cupon.url_qr,
            }
            for cupon in cupones_canjeados
        ]

        # Retorna el historial en formato JSON
        return JsonResponse(historial, safe=False)

    except Exception as e:
        # Manejo de errores en caso de que ocurra un problema
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def verificar_recojo_activo(request, usuario_id):
    if request.method == 'POST':
        try:
            # Buscar un recojo activo para el usuario
            usuario = Usuario.objects.filter(id=usuario_id).first()
            print("ola1")
            if not usuario:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

            # Obtener el gestor de plan del usuario
            gestor_plan = GestorPlan.objects.filter(usuario=usuario).last()
            print("ola2")
            if not gestor_plan:
                print("ola")
                return JsonResponse({'error': 'No se encontró un plan asociado para el usuario'}, status=404)

           
            
            recojo_activo = Recojo.objects.filter(gestor_plan__usuario__id=usuario_id, activo=True).exists()
            print(recojo_activo)
            return JsonResponse({'recojo_activo': recojo_activo})
        except Recojo.DoesNotExist:
            return JsonResponse({'recojo_activo': False})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido.'}, status=405)

#### Sprint 3    
def generate_pdf(usuario, gestor_plan):
    buffer = BytesIO()
    
    p = canvas.Canvas(buffer, pagesize=A5)  # Formato A5

    # Titulo
    p.setFont("Helvetica-Bold", 16)  # Tamaño de fuente
    p.setFillColor(colors.darkblue)
    p.drawString(70, 400, "Boleta PDF de Recojo Inactivo")

    # Información del usuario y plan
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.black)
    p.drawString(70, 380, f"Nombre: {usuario.nombre} {usuario.apellido}")
    p.drawString(70, 360, f"Plan: {gestor_plan.plan.nombre}")
    p.drawString(70, 340, f"Fecha de inactivación: {timezone.now().strftime('%d/%m/%Y')}")
    p.drawString(70, 320, f"Puntos asignados: {gestor_plan.plan.puntos_plan}")

    # Finalizar el PDF
    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer

@csrf_exempt
def listar_pagos_no_validados(request):
    # Filtrar solo los pagos no validados
    pagos_no_validados = GestorPlan.objects.filter(validado=False)
    # Serializar los datos
    data = [
        {
            'id': pago.id,
            'usuarioid':pago.usuario.id,
            'usuario': str(pago.usuario),  # Usa el método __str__ de Usuario
            'plan': str(pago.plan),        # Usa el método __str__ de Plan
            'metodo_pago': str(pago.pago), # Usa el método __str__ de Pago
            'recojos_solicitados': pago.recojos_solicitados           
        }
        for pago in pagos_no_validados
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
def validar_pago(request, pago_id):
    if request.method == 'POST':
        try:
            pago = GestorPlan.objects.get(id=pago_id)
            pago.validado = True
            pago.save()
            return JsonResponse({'success': True, 'message': 'Pago validado correctamente.'})
        except GestorPlan.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pago no encontrado.'}, status=404)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

# Función para generar un PDF con estilo de voucher
def generar_pdf_voucher(usuario):
    # Datos para el contexto
    fecha_emision = localtime(datetime.now().strftime("%d/%m/%Y %H:%M"))

    # HTML directamente en la función
    html_string = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Comprobante de Pago</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                color: #333;
            }}
            .header {{
                background-color: #003366;
                color: white;
                text-align: center;
                padding: 20px;
            }}
            .container {{
                padding: 20px;
            }}
            .table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            .table th, .table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .table th {{
                background-color: #E8E8E8;
                color: #003366;
            }}
            .footer {{
                margin-top: 20px;
                font-size: 12px;
                text-align: center;
            }}
            .foot{{
                text-align: center;
            }}
        </style>
    </head>
    <body>

    <div class="header">
        <h1>COMPROBANTE DE PAGO</h1>
    </div>

    <div class="container">
        <h2 class ="foot">Detalles del Pago</h2>
        <table class="table">
            <tr>
                <th>Nombre:</th>
                <td>{usuario['nombre']} {usuario['apellido']}</td>
            </tr>
            <tr>
                <th>DNI:</th>
                <td>{usuario['DNI']}</td>
            </tr>
            <tr>
                <th>Número de contacto:</th>
                <td>{usuario['numero_contacto']}</td>
            </tr>
            <tr>
                <th>Email:</th>
                <td>{usuario['email']}</td>
            </tr>
            <tr>
                <th>Dirección:</th>
                <td>{usuario['direccion']}</td>
            </tr>
            <tr>
                <th>Plan contratado:</th>
                <td>{usuario['gestorplan__plan__nombre']}</td>
            </tr>
            <tr>
                <th>Precio del plan:</th>
                <td>S/ {usuario['gestorplan__plan__precio']}</td>
            </tr>
            <tr>
                <th>Fecha de emisión:</th>
                <td>{fecha_emision}</td>
            </tr>
        </table>

        <p class ="foot">¡Gracias por su preferencia! Si tiene alguna duda sobre su pago, no dude en contactarnos.</p>
    </div>

    </body>
    </html>
    """

    # Crear un buffer para almacenar el PDF
    buffer = BytesIO()

    # Convertir el HTML a PDF usando xhtml2pdf
    pisa_status = pisa.CreatePDF(html_string, dest=buffer)

    # Asegúrate de que la conversión fue exitosa
    if pisa_status.err:
        return None

    buffer.seek(0)
    return buffer

@csrf_exempt
def enviar_PDF(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        usuario_id = data.get('usuario_id')

        # Obtener los datos de usuario
        usuarios_data = list(UsuarioClienteService.obtener_usuarios_valido(usuario_id).values(
            'id', 'nombre', 'apellido', 'direccion', 'numero_contacto', 'DNI', 'email',
            'gestorplan__plan__nombre',
            'gestorplan__plan__precio'
        ))

        if not usuarios_data:
            return JsonResponse({'message': 'No se encontraron usuarios para este ID.'}, status=404)

        # Tomar el primer usuario (si hay más de un usuario, deberías decidir cuál escoger)
        usuario = usuarios_data[0]

        # Generar el PDF del voucher
        pdf_buffer = generar_pdf_voucher(usuario)

        # Crear el contenido HTML con estilo profesional
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Helvetica', Arial, sans-serif;
                    background-color: #e0e0e0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }}
                .container {{
                    width: 100%;
                    max-width: 600px;
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    text-align: left;
                }}
                h2 {{
                    color: #003366;
                    font-size: 24px;
                    font-weight: 600;
                    margin-bottom: 20px;
                }}
                p {{
                    font-size: 14px;
                    line-height: 1.6;
                    margin-bottom: 10px;
                }}
                .highlight {{
                    color: #003366;
                    font-weight: bold;
                }}
                .footer {{
                    font-size: 12px;
                    color: #777;
                    text-align: center;
                    margin-top: 30px;
                }}
                .footer a {{
                    color: #003366;
                    text-decoration: none;
                }}
                .footer .company {{
                    font-size: 14px;
                    color: #333;
                }}
                .footer .company a {{
                    font-weight: bold;
                    color: #003366;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Comprobante de Pago - {usuario["nombre"]} {usuario["apellido"]}</h2>
                <p>Estimado(a) {usuario["nombre"]},</p>
                <p>Le informamos que hemos recibido su pago por el plan <span class="highlight">{usuario['gestorplan__plan__nombre']}</span>.</p>
                <p>Adjunto a este correo encontrará el <strong>Comprobante de Pago</strong> en formato PDF, correspondiente a su suscripción.</p>
                <p><strong>Detalles del Pago:</strong></p>
                <ul>
                    <li><strong>Plan contratado:</strong> {usuario['gestorplan__plan__nombre']}</li>
                    <li><strong>Precio:</strong> S/ {usuario['gestorplan__plan__precio']}</li>
                    <li><strong>DNI:</strong> {usuario['DNI']}</li>
                    <li><strong>Fecha de emisión:</strong> {localtime(timezone.now()).strftime('%d/%m/%Y')}</li>
                </ul>
                <p>Para cualquier duda o consulta, no dude en ponerse en contacto con nosotros. Estamos a su disposición para ayudarle.</p>
                <p>Gracias por confiar en nosotros.</p>
                <div class="footer">
                    <p class="company">Atentamente, <br> El equipo de <strong>VerdeUlima</strong></p>
                    <p>Si tiene alguna pregunta, contáctenos en <a href="mailto:verdeulima@gmail.com">verdeulima@gmail.com</a></p>
                    <p>&copy; {timezone.now().year} VerdeUlima. Todos los derechos reservados.</p>
                    <p><a href="">Visite nuestro sitio web</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        # Crear el correo con el contenido HTML
        email = EmailMessage(
            'Comprobante de Pago',
            strip_tags(html_content),  # Versión de texto sin formato como respaldo
            'verdeulima@gmail.com',  # Cambia esto por tu dirección de correo
            [usuario['email']],
        )
        email.attach(f'voucher_{usuario["id"]}.pdf', pdf_buffer.read(), 'application/pdf')

        # Establecer el contenido del correo como HTML
        email.content_subtype = "html"
        email.body = html_content

        # Enviar el correo
        email.send(fail_silently=False)

        return JsonResponse({'message': 'Voucher enviado al correo del usuario.'}, status=200)
    
@csrf_exempt
def ultimas_notificaciones(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            usuario_id = body.get('usuario_id')

            # Verificar si el usuario existe
            usuario = Usuario.objects.filter(id=usuario_id).first()
            if not usuario:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

            # Obtener las últimas 4 notificaciones
            notificaciones = Notificacion.objects.filter(usuario=usuario).order_by('-fecha_creacion')[:4]
            if not notificaciones.exists():
                return JsonResponse({'error': 'No se encontraron notificaciones para este usuario'}, status=404)

            # Construir la respuesta con las notificaciones
            notificaciones_data = []
            for notificacion in notificaciones:
                notificaciones_data.append({
                    'id': notificacion.id,
                    'mensaje': notificacion.mensaje,
                    'fecha_creacion': localtime(notificacion.fecha_creacion).strftime('%Y-%m-%d %H:%M:%S'),
                    'leido': notificacion.leido
                })

            return JsonResponse({'status': 'success', 'notificaciones': notificaciones_data}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)