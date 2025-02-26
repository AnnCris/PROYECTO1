import csv
import xlsxwriter
from io import BytesIO
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import datetime, timedelta

from ventas.models import Venta, DetalleVenta
from productos.models import Producto
from clientes.models import Cliente
from .forms import ReporteVentasForm, ReporteInventarioForm, ReporteClientesForm

@login_required
def index_reportes(request):
    return render(request, 'reportes/index.html')

@login_required
def reporte_ventas(request):

    form = ReporteVentasForm(request.GET or None)
    resultados = None
    

    subtotal_total = 0
    descuento_total = 0
    impuesto_total = 0
    total_total = 0
    
    if form.is_valid():
        fecha_inicio = form.cleaned_data['fecha_inicio']
        fecha_fin = form.cleaned_data['fecha_fin']
        categoria = form.cleaned_data['categoria']
        estado = form.cleaned_data['estado']
        

        fecha_inicio = datetime.combine(fecha_inicio, datetime.min.time())
        fecha_fin = datetime.combine(fecha_fin, datetime.max.time())
        

        ventas = Venta.objects.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin
        )
        

        if estado:
            ventas = ventas.filter(estado=estado)
        

        if categoria:

            detalles = DetalleVenta.objects.filter(
                producto__categoria=categoria
            ).values_list('venta_id', flat=True)
            
            ventas = ventas.filter(id__in=detalles)
        
        resultados = ventas.select_related('cliente').prefetch_related('detalles__producto')

        for venta in resultados:
            subtotal_total += venta.subtotal
            descuento_total += venta.descuento
            impuesto_total += venta.impuesto
            total_total += venta.total
        

        if 'export' in request.GET:
            formato = request.GET.get('format', 'csv')
            return exportar_ventas(resultados, formato)
    
    return render(request, 'reportes/reporte_ventas.html', {
        'form': form,
        'resultados': resultados,
        'subtotal_total': subtotal_total,
        'descuento_total': descuento_total,
        'impuesto_total': impuesto_total,
        'total_total': total_total
    })

@login_required
def reporte_inventario(request):
    form = ReporteInventarioForm(request.GET or None)
    resultados = None
    
    if form.is_valid():
        categoria = form.cleaned_data['categoria']
        stock_bajo = form.cleaned_data['stock_bajo']
        

        productos = Producto.objects.all()
        

        if categoria:
            productos = productos.filter(categoria=categoria)
        
        if stock_bajo:
            productos = productos.filter(stock__lte=F('stock_minimo'))
        

        resultados = productos.annotate(
            ventas_count=Count('detalleventa')
        ).order_by('codigo')
        

        if 'export' in request.GET:
            formato = request.GET.get('format', 'csv')
            return exportar_inventario(resultados, formato)
    
    return render(request, 'reportes/reporte_inventario.html', {
        'form': form,
        'resultados': resultados
    })

@login_required
def reporte_clientes(request):
  
    form = ReporteClientesForm(request.GET or None)
    resultados = None
    
    if form.is_valid():
        activo = form.cleaned_data['activo']
        departamento = form.cleaned_data['departamento']
        

        clientes = Cliente.objects.all()
        

        if activo:
            activo_bool = activo == 'True'
            clientes = clientes.filter(activo=activo_bool)
        
        if departamento:
            clientes = clientes.filter(departamento_documento=departamento)
        
        
        resultados = clientes.annotate(
            total_ventas=Count('ventas'),
            total_gastado=Sum('ventas__total')
        ).order_by('nombres')
        
       
        if 'export' in request.GET:
            formato = request.GET.get('format', 'csv')
            return exportar_clientes(resultados, formato)
    
    return render(request, 'reportes/reporte_clientes.html', {
        'form': form,
        'resultados': resultados
    })



def exportar_ventas(ventas, formato):

    if formato == 'excel':
        return exportar_ventas_excel(ventas)
    return exportar_ventas_csv(ventas)

def exportar_ventas_csv(ventas):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Fecha', 'Cliente', 'Estado', 'Método de Pago', 'Subtotal', 'Descuento', 'Impuesto', 'Total'])
    
    for venta in ventas:
        writer.writerow([
            venta.id,
            venta.fecha.strftime('%d/%m/%Y %H:%M'),
            f"{venta.cliente.nombres} {venta.cliente.apellidos}",
            venta.get_estado_display(),
            venta.get_metodo_pago_display(),
            venta.subtotal,
            venta.descuento,
            venta.impuesto,
            venta.total
        ])
    
    return response

def exportar_ventas_excel(ventas):

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Ventas')
    

    title_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D9E1F2', 'border': 1})
    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm', 'border': 1})
    number_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
    border_format = workbook.add_format({'border': 1})
    

    headers = ['ID', 'Fecha', 'Cliente', 'Estado', 'Método de Pago', 'Subtotal', 'Descuento', 'Impuesto', 'Total']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, title_format)
    

    for row, venta in enumerate(ventas, start=1):
        worksheet.write(row, 0, venta.id, border_format)
        worksheet.write(row, 1, venta.fecha, date_format)
        worksheet.write(row, 2, f"{venta.cliente.nombres} {venta.cliente.apellidos}", border_format)
        worksheet.write(row, 3, venta.get_estado_display(), border_format)
        worksheet.write(row, 4, venta.get_metodo_pago_display(), border_format)
        worksheet.write(row, 5, float(venta.subtotal), number_format)
        worksheet.write(row, 6, float(venta.descuento), number_format)
        worksheet.write(row, 7, float(venta.impuesto), number_format)
        worksheet.write(row, 8, float(venta.total), number_format)

    for i, width in enumerate([10, 20, 30, 15, 20, 15, 15, 15, 15]):
        worksheet.set_column(i, i, width)
    
    workbook.close()
    

    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.xlsx"'
    
    return response

def exportar_inventario(productos, formato):

    if formato == 'excel':
        return exportar_inventario_excel(productos)
    return exportar_inventario_csv(productos)

def exportar_inventario_csv(productos):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_inventario.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Código', 'Nombre', 'Categoría', 'Precio', 'Stock Actual', 'Stock Mínimo', 'Estado', 'Ventas'])
    
    for producto in productos:

        if producto.stock <= 0:
            estado = 'Sin Stock'
        elif producto.stock <= producto.stock_minimo:
            estado = 'Stock Bajo'
        else:
            estado = 'Normal'
            
        writer.writerow([
            producto.codigo,
            producto.nombre,
            producto.get_categoria_display(),
            producto.precio,
            producto.stock,
            producto.stock_minimo,
            estado,
            producto.ventas_count
        ])
    
    return response

def exportar_inventario_excel(productos):

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Inventario')
    

    title_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D9E1F2', 'border': 1})
    number_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
    border_format = workbook.add_format({'border': 1})
    
    estado_normal = workbook.add_format({'border': 1, 'bg_color': '#C6EFCE', 'font_color': '#006100'})
    estado_bajo = workbook.add_format({'border': 1, 'bg_color': '#FFEB9C', 'font_color': '#9C5700'})
    estado_sin_stock = workbook.add_format({'border': 1, 'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    

    headers = ['Código', 'Nombre', 'Categoría', 'Precio', 'Stock Actual', 'Stock Mínimo', 'Estado', 'Ventas']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, title_format)
    

    for row, producto in enumerate(productos, start=1):
        worksheet.write(row, 0, producto.codigo, border_format)
        worksheet.write(row, 1, producto.nombre, border_format)
        worksheet.write(row, 2, producto.get_categoria_display(), border_format)
        worksheet.write(row, 3, float(producto.precio), number_format)
        worksheet.write(row, 4, producto.stock, border_format)
        worksheet.write(row, 5, producto.stock_minimo, border_format)
        
        if producto.stock <= 0:
            estado = 'Sin Stock'
            estado_format = estado_sin_stock
        elif producto.stock <= producto.stock_minimo:
            estado = 'Stock Bajo'
            estado_format = estado_bajo
        else:
            estado = 'Normal'
            estado_format = estado_normal
            
        worksheet.write(row, 6, estado, estado_format)
        worksheet.write(row, 7, producto.ventas_count, border_format)
    

    for i, width in enumerate([15, 30, 20, 15, 15, 15, 15, 10]):
        worksheet.set_column(i, i, width)
    
    workbook.close()
    

    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_inventario.xlsx"'
    
    return response

def exportar_clientes(clientes, formato):

    if formato == 'excel':
        return exportar_clientes_excel(clientes)
    return exportar_clientes_csv(clientes)

def exportar_clientes_csv(clientes):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_clientes.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Nombre', 'Tipo Documento', 'Nro. Documento', 'Departamento', 'Teléfono', 'Email', 'Estado', 'Total Ventas', 'Total Gastado'])
    
    for cliente in clientes:
        writer.writerow([
            f"{cliente.nombres} {cliente.apellidos}",
            cliente.get_tipo_documento_display(),
            cliente.nro_documento,
            cliente.get_departamento_documento_display(),
            cliente.telefono,
            cliente.email or '-',
            'Activo' if cliente.activo else 'Inactivo',
            cliente.total_ventas or 0,
            cliente.total_gastado or 0
        ])
    
    return response

def exportar_clientes_excel(clientes):

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Clientes')
    

    title_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D9E1F2', 'border': 1})
    number_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
    border_format = workbook.add_format({'border': 1})
    
    estado_activo = workbook.add_format({'border': 1, 'bg_color': '#C6EFCE', 'font_color': '#006100'})
    estado_inactivo = workbook.add_format({'border': 1, 'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    

    headers = ['Nombre', 'Tipo Documento', 'Nro. Documento', 'Departamento', 'Teléfono', 'Email', 'Estado', 'Total Ventas', 'Total Gastado']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, title_format)
    

    for row, cliente in enumerate(clientes, start=1):
        worksheet.write(row, 0, f"{cliente.nombres} {cliente.apellidos}", border_format)
        worksheet.write(row, 1, cliente.get_tipo_documento_display(), border_format)
        worksheet.write(row, 2, cliente.nro_documento, border_format)
        worksheet.write(row, 3, cliente.get_departamento_documento_display(), border_format)
        worksheet.write(row, 4, cliente.telefono, border_format)
        worksheet.write(row, 5, cliente.email or '-', border_format)
        

        estado = 'Activo' if cliente.activo else 'Inactivo'
        estado_format = estado_activo if cliente.activo else estado_inactivo
        worksheet.write(row, 6, estado, estado_format)
        
        worksheet.write(row, 7, cliente.total_ventas or 0, border_format)
        worksheet.write(row, 8, float(cliente.total_gastado or 0), number_format)
    
    for i, width in enumerate([30, 20, 20, 15, 15, 25, 15, 15, 15]):
        worksheet.set_column(i, i, width)
    
    workbook.close()
    

    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_clientes.xlsx"'
    
    return response