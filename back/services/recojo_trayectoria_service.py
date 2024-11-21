from back.models import Recojo_trayectoria, Trayectoria, Notificacion
from django.utils import timezone

class RecojoTrayectoriaService:

    @staticmethod
    def siguiente(recojo, administrador, usuario, nueva_trayectoria_id, estado_mensaje):
        trayectoria_obj = Trayectoria.objects.get(id=nueva_trayectoria_id)
        Recojo_trayectoria.objects.create(
            estado_ingreso=timezone.localtime(),
            recojo=recojo,
            trayectoria=trayectoria_obj,
            administrador=administrador
        )
        Notificacion.objects.create(
            usuario=usuario,
            administrador=administrador,
            mensaje=f"El estado de su pedido ha cambiado a '{estado_mensaje}'."
        )

    @staticmethod
    def retroceder(recojo, administrador, usuario):
        # Obtener la trayectoria actual
        trayectoria_actual = Recojo_trayectoria.objects.filter(recojo=recojo).last()
        if not trayectoria_actual:
            raise ValueError("No se encontró una trayectoria asociada al recojo.")

        # Obtener el estado actual
        estado_actual = int(trayectoria_actual.trayectoria.estado)

        # Verificar si se puede retroceder
        if estado_actual <= 1:
            raise ValueError("El estado no puede retroceder más.")

        # Retroceder el estado
        nuevo_estado = estado_actual - 1
        nueva_trayectoria = Trayectoria.objects.get(estado=nuevo_estado)

        # Eliminar la trayectoria actual
        trayectoria_actual.delete()

        # Crear una nueva trayectoria con el estado retrocedido
        Recojo_trayectoria.objects.create(
            estado_ingreso=timezone.localtime(),
            recojo=recojo,
            trayectoria=nueva_trayectoria,
            administrador=administrador if nuevo_estado > 1 else None
        )

        # Mensajes personalizados según el nuevo estado
        mensajes_personalizados = {
            '1': "Su pedido ha regresado al estado original.",
            '2': "Su pedido ha regresado al estado 'En preparación'.",
            '3': "Su pedido ha regresado al estado 'En camino'.",
        }
        mensaje = mensajes_personalizados.get(str(nuevo_estado), "El estado de su pedido ha cambiado.")

        # Crear una notificación para el usuario
        Notificacion.objects.create(
            usuario=usuario,
            administrador=administrador,
            mensaje=mensaje
        )
