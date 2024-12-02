from back.models import Pago, GestorPlan, Notificacion

class PagoService:

    @staticmethod
    def crear_pago(estado, metodo_pago, fecha_pago, monto_pago):
        # Crear una instancia del modelo Pago
        nuevo_pago = Pago(
            estado=estado,
            metodo_pago=metodo_pago,
            fecha_pago=fecha_pago,
            monto_pago=monto_pago,
        )
        nuevo_pago.save()
        return nuevo_pago
    
    @staticmethod
    def validar_pago(pago_id):
        try:
            gestor_plan = GestorPlan.objects.get(id=pago_id)
            
            gestor_plan.validado = True
            gestor_plan.save()

            usuario = gestor_plan.usuario
            Notificacion.objects.create(
                usuario=usuario,
                administrador=None,
                mensaje="Su pago ha sido validado exitosamente. ¡Gracias por usar nuestro servicio!"
            )

            return {'success': True, 'message': 'Pago validado correctamente.'}
        except GestorPlan.DoesNotExist:
            return {'success': False, 'message': 'Pago no encontrado.'}