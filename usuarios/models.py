
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

class UsuarioPersonalizado(AbstractUser):
    email = models.EmailField(unique=True)
    rol = models.ForeignKey(
        Rol, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='usuarios'
    )

    def __str__(self):
        return self.username
    
    def es_administrador(self):
        return self.rol and self.rol.nombre == 'Administrador'

    def es_empleado(self):
        return self.rol and self.rol.nombre == 'Empleado'

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'