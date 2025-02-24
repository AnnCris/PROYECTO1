from django.db import models

class Producto(models.Model):
    CATEGORIAS = [
        ('EL', 'Electrónicos'),
        ('PC', 'Computadoras'),
        ('MV', 'Móviles'),
        ('AC', 'Accesorios'),
        ('CM', 'Componentes'),
        ('RD', 'Redes'),
        ('SW', 'Software'),
        ('OT', 'Otros'),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=2, choices=CATEGORIAS)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"