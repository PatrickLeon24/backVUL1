from back.models import Pago

class PagoService:

    @staticmethod
    def crear_pago(estado, metodo_pago, fecha_pago):
        # Crear una instancia del modelo Pago
        nuevo_pago = Pago(
            estado=estado,
            metodo_pago=metodo_pago,
            fecha_pago=fecha_pago
        )
        nuevo_pago.save()
        return nuevo_pago