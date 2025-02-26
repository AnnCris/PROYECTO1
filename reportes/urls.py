from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.index_reportes, name='index'),
    path('ventas/', views.reporte_ventas, name='ventas'),
    path('inventario/', views.reporte_inventario, name='inventario'),
    path('clientes/', views.reporte_clientes, name='clientes'),
]