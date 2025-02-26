
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ReporteGenerado(models.Model):
    TIPOS = [
        ('VENTAS', 'Reporte de Ventas'),
        ('INVENTARIO', 'Reporte de Inventario'),
        ('CLIENTES', 'Reporte de Clientes'),
        ('FINANCIERO', 'Reporte Financiero'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, choices=TIPOS)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reportes')
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    parametros = models.JSONField(default=dict)  # Guardar los filtros usados
    archivo = models.FileField(upload_to='reportes/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha_generacion.strftime('%d/%m/%Y')}"