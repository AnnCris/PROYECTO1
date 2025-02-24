from django.db import models

class Cliente(models.Model):
    TIPOS_DOCUMENTO = [
        ('CI', 'Carnet de Identidad'),
        ('NIT', 'NIT'),
    ]

    DEPARTAMENTOS = [
        ('LP', 'La Paz'),
        ('CB', 'Cochabamba'),
        ('SC', 'Santa Cruz'),
        ('OR', 'Oruro'),
        ('PT', 'Potosí'),
        ('CH', 'Chuquisaca'),
        ('TJ', 'Tarija'),
        ('BE', 'Beni'),
        ('PD', 'Pando'),
    ]

    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    tipo_documento = models.CharField(max_length=3, choices=TIPOS_DOCUMENTO)
    nro_documento = models.CharField(max_length=20, unique=True)
    complemento = models.CharField(max_length=5, blank=True, null=True, help_text="Complemento del CI (opcional)")
    departamento_documento = models.CharField(max_length=2, choices=DEPARTAMENTOS)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.nro_documento}"

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-fecha_registro']