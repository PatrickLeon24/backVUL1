from back.models import Plan

class PlanService:

    @staticmethod
    def obtener_planes(precio_min=None, precio_max=None, frecuencia_recojo=None):
        # Iniciar consulta base
        planes = Plan.objects.all()

        # Aplicar filtros si están presentes
        if precio_min is not None:
            planes = planes.filter(precio__gte=precio_min)
        if precio_max is not None:
            planes = planes.filter(precio__lte=precio_max)
        if frecuencia_recojo is not None:
            planes = planes.filter(frecuencia_recojo=frecuencia_recojo)

        # Transformar los planes a formato JSON
        planes_data = []
        for plan in planes:
            plan_data = {
                "plan_id": plan.id,
                "nombre": plan.nombre,
                "descripcion": plan.descripcion,
                "imagen": plan.imagen,
                "precio": plan.precio,
                "aserrin": plan.aserrin,
                "baldes": plan.baldes,
                "duracion": plan.duracion,
                "frecuencia_recojo": plan.frecuencia_recojo,
                "cantidad_compostaje": plan.cantidad_compostaje,
                "puntos_plan": plan.puntos_plan,
            }
            planes_data.append(plan_data)
        return planes_data