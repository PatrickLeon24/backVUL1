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