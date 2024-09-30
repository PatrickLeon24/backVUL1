from django.urls import path
from . import views
urlpatterns = [
    path("prueba", views.prueba),
    path("register", views.registrar_usuario),
    path("planesRecojo", views.obtener_planes_recojo),
    path("planes/<int:usuario_id>/",views.obtener_plan_contratado)
     ]