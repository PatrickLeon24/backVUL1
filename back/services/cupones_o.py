from back.models import Cupon

class CuponesO:

    @staticmethod
    def ObtenerCupones():
        cupones = Cupon.objects.all()
        cuponesData = []
        for cupon in cupones:
            cupon_data = {
                "id": cupon.id,
                "costo_puntos": cupon.costo_puntos,
                "local": cupon.local,
                "descripcion": cupon.descripcion,
                "descuento": cupon.descuento,
                "imagen": cupon.imagen,
            }
            cuponesData.append(cupon_data)
        return cuponesData
