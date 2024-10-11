from back.models import Plan

class PlanService:

    @staticmethod
    def obtener_planes():
        planes = Plan.objects.all()
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
        
