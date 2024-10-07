from back.models import Plan, Usuario, GestorPlan

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
    
    @staticmethod
    def obtener_plan_contratado(usuario_id):
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            gestor_plan = GestorPlan.objects.filter(usuario=usuario).first()

            if gestor_plan and gestor_plan.plan:
                plan = gestor_plan.plan
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
                return plan_data
            else:
                return {"error": "El usuario no tiene un plan contratado."}
        except Usuario.DoesNotExist:
            return {"error": "Usuario no encontrado."}
        except Exception as e:
            return {"error": str(e)}
        
