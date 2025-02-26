from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Cliente
from .forms import ClienteForm
from usuarios.decorators import rol_requerido

@login_required
def lista_clientes(request):
    clientes = Cliente.objects.all()
    form = ClienteForm()
    return render(request, 'clientes/lista_clientes.html', {
        'clientes': clientes,
        'form': form
    })

@login_required
@require_http_methods(["POST"])
def crear_cliente(request):
    try:
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'message': 'Cliente creado exitosamente',
                'id': cliente.id
            })
        return JsonResponse({'error': form.errors}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)



@login_required
def detalle_cliente(request, cliente_id):
    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)
        data = {
            'nombres': cliente.nombres,
            'apellidos': cliente.apellidos,
            'tipo_documento': cliente.tipo_documento,
            'nro_documento': cliente.nro_documento,
            'complemento': cliente.complemento,
            'departamento_documento': cliente.departamento_documento,
            'direccion': cliente.direccion,
            'telefono': cliente.telefono,
            'email': cliente.email,
            'activo': cliente.activo
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
@require_http_methods(["PUT"])
def actualizar_cliente(request, cliente_id):
    import json
    cliente = get_object_or_404(Cliente, id=cliente_id)
    try:

        data = json.loads(request.body)
        form = ClienteForm(data, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'message': 'Cliente actualizado exitosamente',
                'cliente': {
                    'id': cliente.id,
                    'nombres': cliente.nombres,
                    'apellidos': cliente.apellidos,
                    'tipo_documento': cliente.tipo_documento,
                    'nro_documento': cliente.nro_documento,
                    'departamento_documento': cliente.get_departamento_documento_display(),
                    'telefono': cliente.telefono,
                    'email': cliente.email,
                    'activo': cliente.activo
                }
            })
        return JsonResponse({'error': form.errors}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["DELETE"])
def eliminar_cliente(request, cliente_id):
    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)
        cliente.delete()
        return JsonResponse({'message': 'Cliente eliminado exitosamente'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)