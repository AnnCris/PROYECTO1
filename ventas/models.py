from django.db import models
from django.conf import settings
from clientes.models import Cliente
from productos.models import Producto
from django.utils import timezone

class Venta(models.Model):
    ESTADOS = [
        ('PD', 'Pendiente'),
        ('PG', 'Pagado'),
        ('ET', 'Entregado'),
        ('CN', 'Cancelado'),
    ]
    
    METODOS_PAGO = [
        ('EF', 'Efectivo'),
        ('TC', 'Tarjeta de Crédito'),
        ('TD', 'Tarjeta de Débito'),
        ('TR', 'Transferencia'),
        ('QR', 'Código QR'),
        ('OT', 'Otro'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ventas')
    fecha = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=2, choices=ESTADOS, default='PD')
    metodo_pago = models.CharField(max_length=2, choices=METODOS_PAGO, default='EF')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    notas = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']
        
    def __str__(self):
        return f"Venta #{self.id} - {self.cliente.nombre}"
    
    def calcular_totales(self):
        """Calcula los totales basados en los detalles de venta"""
        detalles = self.detalles.all()
        self.subtotal = sum(detalle.subtotal for detalle in detalles)
        self.total = self.subtotal - self.descuento + self.impuesto
        return self.total
    
    def actualizar_stock(self):
        """Actualiza el stock de los productos después de confirmar la venta"""
        for detalle in self.detalles.all():
            producto = detalle.producto
            producto.stock -= detalle.cantidad
            producto.save()

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Detalle de venta'
        verbose_name_plural = 'Detalles de venta'
        unique_together = ('venta', 'producto')
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"