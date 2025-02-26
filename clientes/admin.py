from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'tipo_documento', 'nro_documento', 'telefono', 'email', 'activo')
    list_filter = ('tipo_documento', 'departamento_documento', 'activo')
    search_fields = ('nombres', 'apellidos', 'nro_documento', 'telefono', 'email')
    list_editable = ('telefono', 'email', 'activo')
    readonly_fields = ('fecha_registro', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información personal', {
            'fields': ('nombres', 'apellidos', 'telefono', 'email')
        }),
        ('Documentación', {
            'fields': ('tipo_documento', 'nro_documento', 'complemento', 'departamento_documento')
        }),
        ('Dirección', {
            'fields': ('direccion',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fechas', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )