from django.contrib import admin
from .models import ReporteGenerado

@admin.register(ReporteGenerado)
class ReporteGeneradoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'usuario', 'fecha_generacion')
    list_filter = ('tipo', 'fecha_generacion')
    search_fields = ('nombre', 'usuario__username')
    readonly_fields = ('fecha_generacion', 'parametros')
    
    fieldsets = (
        ('Información del reporte', {
            'fields': ('nombre', 'tipo', 'usuario')
        }),
        ('Archivo', {
            'fields': ('archivo',)
        }),
        ('Parámetros', {
            'fields': ('parametros',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_generacion',),
            'classes': ('collapse',)
        }),
    )