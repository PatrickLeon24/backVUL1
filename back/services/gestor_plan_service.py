from back.models import Pago, Usuario, Plan, GestorPlan

class GestorPlanService:

    @staticmethod
    def crear_gestor_plan(usuario_id, plan_id, pago_id):
        # Obtener los objetos de Usuario, Plan y Pago
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            plan = Plan.objects.get(id=plan_id)
            pago = Pago.objects.get(id=pago_id)
        except Usuario.DoesNotExist:
            raise Exception("El usuario no existe")
        except Plan.DoesNotExist:
            raise Exception("El plan no existe")
        except Pago.DoesNotExist:
            raise Exception("El pago no existe")
        
        # Crear la nueva instancia de GestorPlan
        gestor_plan = GestorPlan(usuario=usuario, plan=plan, pago=pago)
        gestor_plan.save()

        return gestor_plan
    
    @staticmethod
    def obtener_plan_contratado(usuario_id):
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            gestor_plan = GestorPlan.objects.filter(usuario=usuario, validado=True).last()

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