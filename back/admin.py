from django.contrib import admin
from .models import*

# Registra tus modelos en el panel de administración

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'direccion', 'numero_contacto')
    search_fields = ('nombre', 'apellido')

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'puntaje_acumulado', 'cantidad_residuos_acumulados')
    search_fields = ('email', 'nombre', 'apellido')
    list_filter = ('puntaje_acumulado',)

@admin.register(EstadoServicio)
class EstadoServicioAdmin(admin.ModelAdmin):
    list_display = ('estado',)
    search_fields = ('estado',)

@admin.register(PlanRecojo)
class PlanRecojoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'precio', 'frecuencia_recojo', 'cantidad_compostaje', 'puntos_plan')
    search_fields = ('nombre',)
    list_filter = ('precio',)

@admin.register(ServicioCompostaje)
class ServicioCompostajeAdmin(admin.ModelAdmin):
    list_display = ('fecha_ingreso', 'fecha_salida', 'activo', 'estado', 'usuario', 'plan')
    list_filter = ('estado', 'usuario', 'plan')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('estado', 'metodo_pago', 'fecha_pago', 'servicio')
    list_filter = ('estado', 'metodo_pago')

@admin.register(Puntos)
class PuntosAdmin(admin.ModelAdmin):
    list_display = ('cantidad_de_puntos', 'plan')
    list_filter = ('plan',)

@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ('local', 'descripcion', 'descuento', 'costo_puntos', 'imagen', 'usuario', 'puntos')
    list_filter = ('usuario', 'puntos')