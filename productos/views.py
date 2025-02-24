from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Producto
from .forms import ProductoForm

@login_required
def lista_productos(request):
    productos = Producto.objects.all()
    form = ProductoForm()
    return render(request, 'productos/lista_productos.html', {
        'productos': productos,
        'form': form
    })

@login_required
@require_http_methods(["POST"])
def crear_producto(request):
    try:
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            return JsonResponse({
                'message': 'Producto creado exitosamente',
                'id': producto.id
            })
        return JsonResponse({'error': form.errors}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def detalle_producto(request, producto_id):
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        data = {
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'categoria': producto.categoria,
            'precio': str(producto.precio),
            'stock': producto.stock,
            'stock_minimo': producto.stock_minimo,
            'marca': producto.marca,
            'modelo': producto.modelo,
            'activo': producto.activo
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["PUT"])
def actualizar_producto(request, producto_id):
    import json
    producto = get_object_or_404(Producto, id=producto_id)
    try:
        # Decodificar los datos JSON del body
        data = json.loads(request.body)
        form = ProductoForm(data, instance=producto)
        if form.is_valid():
            producto = form.save()
            return JsonResponse({
                'message': 'Producto actualizado exitosamente',
                'producto': {
                    'id': producto.id,
                    'codigo': producto.codigo,
                    'nombre': producto.nombre,
                    'categoria': producto.get_categoria_display(),
                    'precio': str(producto.precio),
                    'stock': producto.stock,
                    'marca': producto.marca,
                    'activo': producto.activo
                }
            })
        return JsonResponse({'error': form.errors}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["DELETE"])
def eliminar_producto(request, producto_id):
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        producto.delete()
        return JsonResponse({'message': 'Producto eliminado exitosamente'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)