from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
import json

from .models import Venta, DetalleVenta
from productos.models import Producto
from clientes.models import Cliente
from .forms import VentaForm, DetalleVentaForm

@login_required
def lista_ventas(request):
    """Vista para listar todas las ventas con filtros opcionales"""
    # Obtener parámetros de filtro
    estado = request.GET.get('estado', '')
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')
    
    # Filtrar ventas
    ventas = Venta.objects.all()
    
    if estado:
        ventas = ventas.filter(estado=estado)
    
    if fecha_desde:
        ventas = ventas.filter(fecha__date__gte=fecha_desde)
    
    if fecha_hasta:
        ventas = ventas.filter(fecha__date__lte=fecha_hasta)
    
    return render(request, 'ventas/lista_ventas.html', {
        'ventas': ventas,
    })

@login_required
def nueva_venta(request):
    """Vista para crear una nueva venta"""
    clientes = Cliente.objects.filter(activo=True)
    productos = Producto.objects.filter(activo=True, stock__gt=0)
    contexto = {
        'clientes': clientes,
        'productos': productos,
        'form': VentaForm(),
    }
    return render(request, 'ventas/crear_venta.html', contexto)

@login_required
@require_http_methods(["POST"])
def crear_venta(request):
    """Endpoint para crear una venta completa con sus detalles"""
    try:
        with transaction.atomic():
            # Extraer datos principales de la venta
            datos = json.loads(request.body)
            
            # Crear la venta
            venta = Venta(
                cliente_id=datos['cliente_id'],
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
            
            # Crear los detalles de la venta
            detalles = []
            for item in datos['items']:
                producto = get_object_or_404(Producto, id=item['producto_id'])
                
                # Verificar stock disponible
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
                detalles.append(detalle)
            
            # Actualizar stock si la venta está pagada o entregada
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
def detalle_venta(request, venta_id):
    """Vista para ver el detalle de una venta"""
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = venta.detalles.all()
    
    return render(request, 'ventas/detalle_venta.html', {
        'venta': venta,
        'detalles': detalles
    })

@login_required
@require_http_methods(["PUT"])
def actualizar_venta(request, venta_id):
    """Endpoint para actualizar una venta"""
    try:
        with transaction.atomic():
            venta = get_object_or_404(Venta, id=venta_id)
            datos = json.loads(request.body)
            
            # Si cambia de estado a pagado o entregado y no estaba así antes
            estado_anterior = venta.estado
            nuevo_estado = datos['estado']
            
            # Actualizar datos de la venta
            venta.cliente_id = datos['cliente_id']
            venta.estado = nuevo_estado
            venta.metodo_pago = datos['metodo_pago']
            venta.descuento = datos['descuento']
            venta.impuesto = datos['impuesto']
            venta.subtotal = datos['subtotal']
            venta.total = datos['total']
            venta.notas = datos.get('notas', '')
            venta.save()
            
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
    """Endpoint para eliminar una venta"""
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
    """Endpoint para buscar productos por código o nombre"""
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
            'stock': p.stock
        })
    
    return JsonResponse({'productos': resultado})

@login_required
@require_http_methods(["GET"])
def obtener_producto(request, producto_id):
    """Endpoint para obtener los datos de un producto específico"""
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        return JsonResponse({
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'stock': producto.stock
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)