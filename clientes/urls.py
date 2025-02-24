from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.lista_clientes, name='lista_clientes'),
    path('crear/', views.crear_cliente, name='crear_cliente'),
    path('actualizar/<int:cliente_id>/', views.actualizar_cliente, name='actualizar_cliente'),
    path('eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('detalle/<int:cliente_id>/', views.detalle_cliente, name='detalle_cliente')
]