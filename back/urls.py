from django.urls import path
from . import views
urlpatterns = [
    path("iniciar_sesion", views.inicio_sesion),
    path("tipos-usuario", views.obtener_tipos_usuario),
    path("register", views.registrar_usuario),
    path("planesRecojo", views.obtener_planes_recojo),
    path("planes/<int:usuario_id>/",views.obtener_plan_usuario),
    path("cupones", views.obtener_cupons),
    path('guardar_cambio_contrasena', views.guardar_cambio_contrasena),
    path('crear_pago', views.crear_pago),
    path('guardar_perfil', views.guardar_perfil),
    path('gestor_plan', views.crear_gestor_plan),
    path('solicitar_recojo', views.iniciar_recojo),
    path('estado_pedido', views.verificar_trayectoria_recojo),
    path('obtener_recojos', views.obtener_recojos),  
    path('puntos/<int:usuario_id>/', views.obtener_puntaje_usuario),
    path('consultar_recojo', views.consultar_recojo),
    path('generar', views.generar_codigo_invitacion)
    ]