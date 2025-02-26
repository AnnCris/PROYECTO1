"""
URL configuration for mi_proyecto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from usuarios import views
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login'), name='root'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.inicio_view, name='inicio'),
    path('inicio/', views.inicio_view, name='inicio'),
    path('gestionar-usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('crear-usuario/', views.crear_usuario, name='crear_usuario'),
    path('actualizar-usuario/<int:usuario_id>/', views.actualizar_usuario, name='actualizar_usuario'),
    path('eliminar-usuario/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('clientes/', include('clientes.urls', namespace='clientes')),
    path('productos/', include('productos.urls', namespace='productos')),
    path('ventas/', include('ventas.urls', namespace='ventas')), 
    path('reportes/', include('reportes.urls', namespace='reportes')),  
]
