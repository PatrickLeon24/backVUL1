from django.contrib import admin
from .models import *

# Registro del modelo Tipo_Usuario
@admin.register(Tipo_Usuario)
class TipoUsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo')
    search_fields = ('tipo',)

# Registro del modelo Usuario
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'email', 'cantidad_residuos_acumulados', 'puntaje_acumulado')
    search_fields = ('nombre', 'apellido', 'email')
    list_filter = ('genero',)

# Registro del modelo Cupon
@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ('id', 'local', 'descripcion', 'costo_puntos', 'descuento')
    search_fields = ('local', 'descripcion')

# Registro del modelo Trayectoria
@admin.register(Trayectoria)
class TrayectoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'estado')
    search_fields = ('estado',)

# Registro del modelo Pago
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'estado', 'metodo_pago', 'fecha_pago')
    search_fields = ('estado', 'metodo_pago')

# Registro del modelo Plan
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'frecuencia_recojo', 'puntos_plan')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('duracion',)

@admin.register(GestorPlan)
class GestorPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'plan', 'pago', 'recojos_solicitados')
    search_fields = ('usuario__email', 'plan__nombre')

# Registro del modelo Recojo
@admin.register(Recojo)
class RecojoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_ingreso', 'fecha_salida', 'activo', 'gestor_plan')
    list_filter = ('activo',)
    search_fields = ('fecha_ingreso', 'fecha_salida')

# Registro del modelo Recojo_trayectoria
@admin.register(Recojo_trayectoria)
class RecojoTrayectoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'estado_ingreso', 'recojo', 'trayectoria')
    search_fields = ('estado_ingreso', 'recojo')