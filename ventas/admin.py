from django.contrib import admin
from .models import Venta, DetalleVenta

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    readonly_fields = ('subtotal',)
    autocomplete_fields = ('producto',)

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'estado', 'metodo_pago', 'total')
    list_filter = ('estado', 'metodo_pago', 'fecha')
    search_fields = ('cliente__nombres', 'cliente__apellidos', 'cliente__nro_documento')
    readonly_fields = ('subtotal', 'total', 'fecha_creacion', 'fecha_actualizacion')
    autocomplete_fields = ('cliente', 'usuario')
    inlines = [DetalleVentaInline]
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información básica', {
            'fields': ('cliente', 'usuario', 'fecha', 'estado', 'metodo_pago')
        }),
        ('Montos', {
            'fields': ('subtotal', 'descuento', 'impuesto', 'total')
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
        ('Fechas del sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es una nueva venta
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('venta__estado',)
    search_fields = ('venta__id', 'producto__nombre')
    readonly_fields = ('subtotal',)
    autocomplete_fields = ('venta', 'producto')