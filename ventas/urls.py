from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [

    path('', views.lista_ventas, name='lista_ventas'),
    path('nueva/', views.nueva_venta, name='nueva_venta'),
    path('detalle/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
    path('editar/<int:venta_id>/', views.editar_venta, name='editar_venta'),
    path('crear/', views.crear_venta, name='crear_venta'),
    path('actualizar/<int:venta_id>/', views.actualizar_venta, name='actualizar_venta'),
    path('eliminar/<int:venta_id>/', views.eliminar_venta, name='eliminar_venta'),
    path('buscar-producto/', views.buscar_producto, name='buscar_producto'),
    path('obtener-producto/<int:producto_id>/', views.obtener_producto, name='obtener_producto'),
    path('buscar-cliente/', views.buscar_cliente, name='buscar_cliente'),
    path('detalle/<int:venta_id>/json/', views.api_detalle_venta, name='api_detalle_venta'),
]