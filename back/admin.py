from django.contrib import admin
from .models import*

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'direccion', 'DNI', 'numero_contacto', 'genero')
    search_fields = ('nombre', 'apellido', 'DNI')
    list_filter = ('genero',)

@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido')

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'puntaje_acumulado', 'cantidad_residuos_acumulados', 'cliente')
    search_fields = ('email',)
    list_filter = ('cliente',)

@admin.register(PlanRecojo)
class PlanRecojoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'frecuencia_recojo', 'cantidad_compostaje', 'puntos_plan')
    search_fields = ('nombre',)
    list_filter = ('frecuencia_recojo',)

@admin.register(GestorPlan)
class GestorPlanAdmin(admin.ModelAdmin):
    list_display = ('plan', 'usuario')

@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ('local', 'descripcion', 'descuento', 'costo_puntos')
    search_fields = ('local', 'descripcion')
    list_filter = ('descuento',)

@admin.register(GestorCupon)
class GestorCuponAdmin(admin.ModelAdmin):
    list_display = ('cupon', 'usuario')

@admin.register(EstadoServicio)
class EstadoServicioAdmin(admin.ModelAdmin):
    list_display = ('estado',)

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('estado', 'metodo_pago', 'fecha_pago')
    list_filter = ('estado', 'metodo_pago')

@admin.register(ServicioCompostaje)
class ServicioCompostajeAdmin(admin.ModelAdmin):
    list_display = ('fecha_ingreso', 'fecha_salida', 'activo', 'estado', 'pago')
    list_filter = ('activo', 'estado')
