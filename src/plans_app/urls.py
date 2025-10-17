from django.urls import path
from . import views


urlpatterns = [
    path('mis/', views.mis_planificaciones, name='mis_planificaciones'),
    path('crear/', views.crear_planificacion, name='crear_planificacion'),
    path('<int:plan_id>/', views.planificacion_detalle, name='planificacion_detalle'),
]
