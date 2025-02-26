from pyexpat.errors import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Count, Sum, F
import json

from .models import Venta, DetalleVenta
from productos.models import Producto
from clientes.models import Cliente
from .forms import VentaForm, DetalleVentaForm

@login_required
def lista_ventas(request):

    estado = request.GET.get('estado', '')
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')
    cliente_id = request.GET.get('cliente', '')

    ventas = Venta.objects.all().select_related('cliente', 'usuario')
    
    if estado:
        ventas = ventas.filter(estado=estado)
    
    if fecha_desde:
        ventas = ventas.filter(fecha__date__gte=fecha_desde)
    
    if fecha_hasta:
        ventas = ventas.filter(fecha__date__lte=fecha_hasta)
        
    if cliente_id:
        ventas = ventas.filter(cliente_id=cliente_id)

    clientes = Cliente.objects.filter(activo=True).order_by('nombres', 'apellidos')
    

    total_ventas = ventas.count()
    monto_total = ventas.aggregate(total=Sum('total'))['total'] or 0
    
    contexto = {
        'ventas': ventas,
        'clientes': clientes,
        'total_ventas': total_ventas,
        'monto_total': monto_total,
        'filtros': {
            'estado': estado,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'cliente_id': cliente_id
        }
    }
    
    return render(request, 'ventas/lista_ventas.html', contexto)

@login_required
def nueva_venta(request):
    clientes = Cliente.objects.filter(activo=True).order_by('nombres', 'apellidos')
    

    productos = Producto.objects.filter(
        activo=True, 
        stock__gt=0
    ).order_by('categoria', 'nombre')

    productos_por_categoria = {}
    for producto in productos:
        categoria = producto.get_categoria_display()
        if categoria not in productos_por_categoria:
            productos_por_categoria[categoria] = []
        productos_por_categoria[categoria].append(producto)
    

    productos_stock_bajo = Producto.objects.filter(
        activo=True,
        stock__gt=0,
        stock__lte=F('stock_minimo')
    ).order_by('nombre')
    
    contexto = {
        'clientes': clientes,
        'productos': productos,
        'productos_por_categoria': productos_por_categoria,
        'productos_stock_bajo': productos_stock_bajo,
        'form': VentaForm(),
    }
    return render(request, 'ventas/crear_venta.html', contexto)

@login_required
@require_http_methods(["POST"])
def crear_venta(request):

    try:
        with transaction.atomic():

            datos = json.loads(request.body)
            

            cliente = get_object_or_404(Cliente, id=datos['cliente_id'], activo=True)
            

            venta = Venta(
                cliente=cliente,
                usuario=request.user,
                estado=datos['estado'],
                metodo_pago=datos['metodo_pago'],
                descuento=datos['descuento'],
                impuesto=datos['impuesto'],
                subtotal=datos['subtotal'],
                total=datos['total'],
                notas=datos.get('notas', '')
            )
            venta.save()
            detalles = []
            for item in datos['items']:
                producto = get_object_or_404(Producto, id=item['producto_id'], activo=True)
                
                if producto.stock < item['cantidad']:
                    raise Exception(f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}")
                
                detalle = DetalleVenta(
                    venta=venta,
                    producto=producto,
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio_unitario'],
                    subtotal=item['subtotal']
                )
                detalle.save()
                detalles.append(detalle)
            
            if venta.estado in ['PG', 'ET']:
                venta.actualizar_stock()
            
            return JsonResponse({
                'success': True,
                'message': 'Venta registrada correctamente',
                'venta_id': venta.id
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def editar_venta(request, venta_id):
    """Vista para editar una venta existente"""
    venta = get_object_or_404(Venta, id=venta_id)
    
    if venta.estado != 'PD':
        messages.error(request, "Solo se pueden editar ventas en estado pendiente")
        return redirect('ventas:detalle_venta', venta_id=venta_id)
    
    clientes = Cliente.objects.filter(activo=True).order_by('nombres', 'apellidos')
    productos = Producto.objects.filter(
        activo=True, 
        stock__gt=0
    ).order_by('categoria', 'nombre')
    

    detalles = venta.detalles.all().select_related('producto')
    
    contexto = {
        'venta': venta,
        'detalles': detalles,
        'clientes': clientes,
        'productos': productos,
        'editando': True
    }
    
    return render(request, 'ventas/editar_venta.html', contexto)

@login_required
def detalle_venta(request, venta_id):
    """Vista para ver el detalle de una venta"""
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = venta.detalles.all().select_related('producto')
    

    cliente = venta.cliente
    

    historial_cliente = Venta.objects.filter(
        cliente=cliente
    ).exclude(
        id=venta_id
    ).order_by('-fecha')[:5]
    
    contexto = {
        'venta': venta,
        'detalles': detalles,
        'cliente': cliente,
        'historial_cliente': historial_cliente
    }
    
    return render(request, 'ventas/detalle_venta.html', contexto)

@login_required
@require_http_methods(["PUT"])
def actualizar_venta(request, venta_id):

    try:
        with transaction.atomic():
            venta = get_object_or_404(Venta, id=venta_id)
            if venta.estado != 'PD':
                return JsonResponse({
                    'success': False,
                    'error': 'Solo se pueden editar ventas en estado pendiente'
                }, status=400)
            
            datos = json.loads(request.body)
            

            estado_anterior = venta.estado
            nuevo_estado = datos['estado']
            venta.cliente_id = datos['cliente_id']
            venta.estado = nuevo_estado
            venta.metodo_pago = datos['metodo_pago']
            venta.descuento = datos['descuento']
            venta.impuesto = datos['impuesto']
            venta.subtotal = datos['subtotal']
            venta.total = datos['total']
            venta.notas = datos.get('notas', '')
            venta.save()

            venta.detalles.all().delete()

            for item in datos['items']:
                producto = get_object_or_404(Producto, id=item['producto_id'])
                
                if producto.stock < item['cantidad']:
                    raise Exception(f"Stock insuficiente para {producto.nombre}")
                
                detalle = DetalleVenta(
                    venta=venta,
                    producto=producto,
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio_unitario'],
                    subtotal=item['subtotal']
                )
                detalle.save()
            
            # Gestionar el stock según cambio de estado
            if estado_anterior not in ['PG', 'ET'] and nuevo_estado in ['PG', 'ET']:
                # Si pasa a pagado o entregado, reducir stock
                venta.actualizar_stock()
            
            return JsonResponse({
                'success': True,
                'message': 'Venta actualizada correctamente'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
@require_http_methods(["DELETE"])
def eliminar_venta(request, venta_id):
    try:
        venta = get_object_or_404(Venta, id=venta_id)
        
        # Solo permitir eliminar ventas en estado pendiente
        if venta.estado != 'PD':
            return JsonResponse({
                'success': False,
                'error': 'Solo se pueden eliminar ventas en estado pendiente'
            }, status=400)
        
        venta.delete()
        return JsonResponse({
            'success': True,
            'message': 'Venta eliminada correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
@require_http_methods(["GET"])
def buscar_producto(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'productos': []})
    
    productos = Producto.objects.filter(
        activo=True, 
        stock__gt=0
    ).filter(
        Q(codigo__icontains=query) | 
        Q(nombre__icontains=query)
    )[:10]
    
    resultado = []
    for p in productos:
        resultado.append({
            'id': p.id,
            'codigo': p.codigo,
            'nombre': p.nombre,
            'precio': str(p.precio),
            'stock': p.stock,
            'categoria': p.get_categoria_display()
        })
    
    return JsonResponse({'productos': resultado})

@login_required
@require_http_methods(["GET"])
def obtener_producto(request, producto_id):
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        return JsonResponse({
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'stock': producto.stock,
            'categoria': producto.get_categoria_display(),
            'marca': producto.marca,
            'modelo': producto.modelo
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def buscar_cliente(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'clientes': []})
    
    clientes = Cliente.objects.filter(
        activo=True
    ).filter(
        Q(nombres__icontains=query) | 
        Q(apellidos__icontains=query) | 
        Q(nro_documento__icontains=query)
    )[:10]
    
    resultado = []
    for c in clientes:
        resultado.append({
            'id': c.id,
            'nombre': f"{c.nombres} {c.apellidos}",
            'documento': f"{c.get_tipo_documento_display()}: {c.nro_documento}",
            'telefono': c.telefono
        })
    
    return JsonResponse({'clientes': resultado})

@login_required
def api_detalle_venta(request, venta_id):
    try:
        venta = get_object_or_404(Venta, id=venta_id)
        detalles = []
        
        for detalle in venta.detalles.all():
            detalles.append({
                'id': detalle.id,
                'producto_id': detalle.producto.id,
                'producto_nombre': f"{detalle.producto.codigo} - {detalle.producto.nombre}",
                'cantidad': detalle.cantidad,
                'precio_unitario': str(detalle.precio_unitario),
                'subtotal': str(detalle.subtotal)
            })
        
        data = {
            'id': venta.id,
            'cliente_id': venta.cliente.id,
            'cliente_nombre': f"{venta.cliente.nombres} {venta.cliente.apellidos}",
            'fecha': venta.fecha.strftime('%Y-%m-%d %H:%M'),
            'estado': venta.estado,
            'metodo_pago': venta.metodo_pago,
            'subtotal': str(venta.subtotal),
            'descuento': str(venta.descuento),
            'impuesto': str(venta.impuesto),
            'total': str(venta.total),
            'notas': venta.notas,
            'detalles': detalles
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)