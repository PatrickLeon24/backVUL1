from back.models import Notificacion
from django.utils import timezone

class RecojoService:

    @staticmethod
    def finalizar(recojo, administrador, usuario, gestor_plan):
        recojo.activo = False
        recojo.fecha_salida = timezone.localtime()
        recojo.save()

        # Verificar si el plan aún existe
        if gestor_plan.plan:
            puntos = gestor_plan.plan.puntos_plan
            mensaje_puntos = f"Se han sumado {puntos} puntos a su cuenta."
        else:
            # Si el plan ha sido eliminado
            puntos = gestor_plan.puntos_backup 
            mensaje_puntos = f"Su plan ya no está disponible, pero se han sumado {puntos} puntos a su cuenta."

        usuario.puntaje_acumulado += puntos
        usuario.save()

        Notificacion.objects.create(
            usuario=usuario,
            administrador=administrador,
            mensaje=f"Su pedido ha sido finalizado correctamente. {mensaje_puntos}"
        )