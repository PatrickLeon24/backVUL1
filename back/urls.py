from django.urls import path
from . import views
urlpatterns = [
    path("iniciar_sesion", views.inicio_sesion),
    path("tipos-usuario", views.obtener_tipos_usuario),
    path("register", views.registrar_usuario),
    path("planesRecojo", views.obtener_planes_recojo),
    path("planes/<int:usuario_id>/",views.obtener_plan_usuario),
    path("cupones", views.obtener_cupons),
     path('guardar_cambio_contrasena', views.guardar_cambio_contrasena)
    ]