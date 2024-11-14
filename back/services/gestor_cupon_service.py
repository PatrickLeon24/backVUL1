import uuid
from back.models import GestorCupon, Cupon, Usuario
from django.utils import timezone

class GestorCuponService:

    @staticmethod
    def generar_url_qr():
        # Generar un UUID único y crear la URL del QR
        unique_id = uuid.uuid4()
        return f"https://verdeulima.com/qr/{unique_id}"

    @staticmethod
    def canjear_cupon(usuario_id, cupon_id):
        try:
            # Obtener el usuario y el cupón
            usuario = Usuario.objects.get(id=usuario_id)
            cupon = Cupon.objects.get(id=cupon_id)

            # Verificar si el usuario tiene suficientes puntos
            if usuario.puntaje_acumulado < cupon.costo_puntos:
                return {'error': 'Puntos insuficientes para canjear el cupón'}

            # Verificar si el cupón está disponible
            if cupon.disponibilidad <= 0:
                return {'error': 'El cupón ya no está disponible'}

            # Descontar los puntos del usuario
            usuario.puntaje_acumulado -= cupon.costo_puntos
            usuario.save()

            # Reducir la disponibilidad del cupón
            cupon.disponibilidad -= 1
            cupon.save()

            # Generar la URL del QR llamando al método separado
            url_qr = GestorCuponService.generar_url_qr()
            fecha_canje = timezone.localtime()

            # Registrar el canje en el modelo GestorCupon con la URL del QR
            GestorCupon.objects.create(usuario=usuario, cupon=cupon, url_qr=url_qr, fecha_canje=fecha_canje)

            return {'mensaje': 'Canje exitoso', 'url_qr': url_qr}

        except Usuario.DoesNotExist:
            return {'error': 'Usuario no encontrado'}
        except Cupon.DoesNotExist:
            return {'error': 'Cupón no encontrado'}
        except Exception as e:
            return {'error': str(e)}