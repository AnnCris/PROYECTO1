from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio', 'stock', 'stock_minimo', 'activo')
    list_filter = ('categoria', 'activo', 'marca')
    search_fields = ('codigo', 'nombre', 'descripcion')
    list_editable = ('precio', 'stock', 'activo')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'categoria')
        }),
        ('Precios y stock', {
            'fields': ('precio', 'stock', 'stock_minimo')
        }),
        ('Detalles adicionales', {
            'fields': ('marca', 'modelo', 'activo')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )