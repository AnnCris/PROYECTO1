from django import forms
from django.utils import timezone
from datetime import datetime, timedelta

class ReporteVentasForm(forms.Form):
    fecha_inicio = forms.DateField(
        label="Fecha Inicio",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date() - timedelta(days=30)
    )
    fecha_fin = forms.DateField(
        label="Fecha Fin",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date()
    )
    categoria = forms.ChoiceField(
        label="Categoría",
        required=False, 
        choices=[('', 'Todas')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    estado = forms.ChoiceField(
        label="Estado",
        required=False, 
        choices=[
            ('', 'Todos'),
            ('PD', 'Pendiente'),
            ('PG', 'Pagado'),
            ('ET', 'Entregado'),
            ('CN', 'Cancelado'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from productos.models import Producto

        categorias = Producto.CATEGORIAS
        self.fields['categoria'].choices += categorias

class ReporteInventarioForm(forms.Form):
    categoria = forms.ChoiceField(
        label="Categoría",
        required=False, 
        choices=[('', 'Todas')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    stock_bajo = forms.BooleanField(
        required=False, 
        label="Solo productos con stock bajo",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from productos.models import Producto

        categorias = Producto.CATEGORIAS
        self.fields['categoria'].choices += categorias

class ReporteClientesForm(forms.Form):
    activo = forms.ChoiceField(
        label="Estado",
        required=False, 
        choices=[
            ('', 'Todos'),
            ('True', 'Activos'),
            ('False', 'Inactivos'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    departamento = forms.ChoiceField(
        label="Departamento",
        required=False, 
        choices=[('', 'Todos')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from clientes.models import Cliente
        departamentos = Cliente.DEPARTAMENTOS
        self.fields['departamento'].choices += departamentos