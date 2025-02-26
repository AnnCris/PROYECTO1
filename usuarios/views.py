import json
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegistroForm
from django.contrib.auth import get_user_model
from .models import UsuarioPersonalizado, Rol
from .decorators import rol_requerido
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

User = get_user_model()


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        

        try:
            user = User.objects.get(email=username_or_email)
            username = user.username
        except User.DoesNotExist:
            username = username_or_email
            

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario/Email o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, 'Por favor, corrija los errores del formulario.')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

@login_required
@rol_requerido(['Administrador'])
def gestionar_usuarios(request):
    usuarios = UsuarioPersonalizado.objects.all()
    roles = Rol.objects.all()
    
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        rol_id = request.POST.get('rol_id')
        
        try:
            usuario = UsuarioPersonalizado.objects.get(id=usuario_id)
            rol = Rol.objects.get(id=rol_id)
            usuario.rol = rol
            usuario.save()
            messages.success(request, f'Rol actualizado para {usuario.username}')
        except Exception as e:
            messages.error(request, 'Error al actualizar el rol')
        
    return render(request, 'usuarios/gestionar_usuarios.html', {
        'usuarios': usuarios,
        'roles': roles
    })


@login_required
def inicio_view(request):
    from datetime import datetime, timedelta
    from django.db.models import Sum, Count, Q, F  
    from django.utils import timezone
    from ventas.models import Venta
    from productos.models import Producto
    from clientes.models import Cliente

    hoy = timezone.now().date()
    inicio_del_dia = datetime.combine(hoy, datetime.min.time())
    fin_del_dia = datetime.combine(hoy, datetime.max.time())
    

    inicio_del_mes = datetime(hoy.year, hoy.month, 1, 0, 0, 0)

    if hoy.month == 12:
        fin_del_mes = datetime(hoy.year + 1, 1, 1, 0, 0, 0) - timedelta(days=1)
    else:
        fin_del_mes = datetime(hoy.year, hoy.month + 1, 1, 0, 0, 0) - timedelta(days=1)
    fin_del_mes = datetime.combine(fin_del_mes.date(), datetime.max.time())
    

    stats = {

        'ventas_dia': Venta.objects.filter(
            fecha__gte=inicio_del_dia,
            fecha__lte=fin_del_dia
        ).aggregate(total=Sum('total'))['total'] or 0,
        

        'ventas_mes': Venta.objects.filter(
            fecha__gte=inicio_del_mes,
            fecha__lte=fin_del_mes
        ).aggregate(total=Sum('total'))['total'] or 0,
        

        'total_productos': Producto.objects.filter(activo=True).count(),
        
        'clientes_activos': Cliente.objects.filter(activo=True).count(),
        
        'productos_stock_bajo': Producto.objects.filter(
            activo=True,
            stock__lte=F('stock_minimo')
        ).count(),
        

        'ventas_pendientes': Venta.objects.filter(estado='PD').count()
    }
    

    ventas_recientes = Venta.objects.select_related('cliente').order_by('-fecha')[:10]
    

    ventas_tabla = []
    for venta in ventas_recientes:
        primer_producto = venta.detalles.select_related('producto').first()
        producto_nombre = primer_producto.producto.nombre if primer_producto else "Múltiples productos"
        
        ventas_tabla.append({
            'id': venta.id,
            'cliente': f"{venta.cliente.nombres} {venta.cliente.apellidos}",
            'producto': producto_nombre,
            'fecha': venta.fecha,
            'monto': venta.total,
            'estado': venta.get_estado_display()
        })
    
    context = {
        'stats': stats,
        'ventas_recientes': ventas_tabla,
        'now': timezone.now() 
    }
    
    if request.user.es_administrador():
        return render(request, 'usuarios/inicio.html', context)
    elif request.user.es_empleado():
        return render(request, 'usuarios/dashboard_empleado.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
@rol_requerido(['Administrador'])
def gestionar_usuarios(request):
    usuarios = UsuarioPersonalizado.objects.all()
    roles = Rol.objects.all()
    form = RegistroForm()
    
    return render(request, 'usuarios/gestionar_usuarios.html', {
        'usuarios': usuarios,
        'roles': roles,
        'form': form
    })


@login_required
@rol_requerido(['Administrador'])
@require_http_methods(["POST"])
def crear_usuario(request):
    try:

        data = json.loads(request.body)
        

        form_data = {
            'username': data.get('username'),
            'email': data.get('email'),
            'password1': data.get('password1'),
            'password2': data.get('password2'),
            'rol': data.get('rol_id'),
            'is_active': data.get('is_active', True)
        }
        
        form = RegistroForm(form_data)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.rol_id = form_data['rol']  
            usuario.is_active = form_data['is_active']
            usuario.save()
            
            return JsonResponse({
                'message': 'Usuario creado exitosamente',
                'usuario': {
                    'id': usuario.id,
                    'username': usuario.username,
                    'email': usuario.email,
                    'rol': usuario.rol.nombre if usuario.rol else None,
                    'is_active': usuario.is_active
                }
            })
        else:

            errores = {}
            for field, error_list in form.errors.items():
                errores[field] = list(error_list)
            return JsonResponse({'error': errores}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
@rol_requerido(['Administrador'])
@require_http_methods(["PUT"])
def actualizar_usuario(request, usuario_id):
    import json
    usuario = get_object_or_404(UsuarioPersonalizado, id=usuario_id)
    
    try:
        datos = json.loads(request.body)
        username = datos.get('username')
        email = datos.get('email')
        rol_id = datos.get('rol_id')
        is_active = datos.get('is_active')
        

        if UsuarioPersonalizado.objects.exclude(id=usuario_id).filter(username=username).exists():
            return JsonResponse({'error': 'El nombre de usuario ya existe'}, status=400)
        if UsuarioPersonalizado.objects.exclude(id=usuario_id).filter(email=email).exists():
            return JsonResponse({'error': 'El email ya existe'}, status=400)

        if username:
            usuario.username = username
        if email:
            usuario.email = email
        if is_active is not None:
            usuario.is_active = is_active
        
        if rol_id:
            rol = get_object_or_404(Rol, id=rol_id)
            usuario.rol = rol
            
        usuario.save()
        return JsonResponse({
            'message': 'Usuario actualizado exitosamente',
            'usuario': {
                'id': usuario.id,
                'username': usuario.username,
                'email': usuario.email,
                'is_active': usuario.is_active,
                'rol': usuario.rol.nombre if usuario.rol else None
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
@rol_requerido(['Administrador'])
@require_http_methods(["DELETE"])
def eliminar_usuario(request, usuario_id):
    try:
        usuario = get_object_or_404(UsuarioPersonalizado, id=usuario_id)
        if usuario == request.user:
            return JsonResponse({'error': 'No puedes eliminar tu propio usuario'}, status=400)
        usuario.delete()
        return JsonResponse({'message': 'Usuario eliminado exitosamente'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def dashboard_empleado(request):
    from datetime import datetime, timedelta
    from django.db.models import Sum, Count, F, Q
    from django.utils import timezone
    from ventas.models import Venta
    from productos.models import Producto
    from clientes.models import Cliente
    
    # Obtener fecha actual y comienzo del mes
    hoy = timezone.now().date()
    inicio_del_dia = datetime.combine(hoy, datetime.min.time())
    fin_del_dia = datetime.combine(hoy, datetime.max.time())
    
    # Para el mes actual
    inicio_del_mes = datetime(hoy.year, hoy.month, 1, 0, 0, 0)
    # Último día del mes
    if hoy.month == 12:
        fin_del_mes = datetime(hoy.year + 1, 1, 1, 0, 0, 0) - timedelta(days=1)
    else:
        fin_del_mes = datetime(hoy.year, hoy.month + 1, 1, 0, 0, 0) - timedelta(days=1)
    fin_del_mes = datetime.combine(fin_del_mes.date(), datetime.max.time())
    
    # Estadísticas para el dashboard
    stats = {
        # Ventas del día
        'ventas_dia': Venta.objects.filter(
            fecha__gte=inicio_del_dia,
            fecha__lte=fin_del_dia
        ).aggregate(total=Sum('total'))['total'] or 0,
        
        # Ventas del mes
        'ventas_mes': Venta.objects.filter(
            fecha__gte=inicio_del_mes,
            fecha__lte=fin_del_mes
        ).aggregate(total=Sum('total'))['total'] or 0,
        
        # Total de productos
        'total_productos': Producto.objects.filter(activo=True).count(),
        
        # Clientes activos
        'clientes_activos': Cliente.objects.filter(activo=True).count(),
        
        # Productos con stock bajo
        'productos_stock_bajo': Producto.objects.filter(
            activo=True,
            stock__lte=F('stock_minimo')
        ).count(),
    }
    
    # Obtener ventas recientes
    ventas_recientes = Venta.objects.select_related('cliente').order_by('-fecha')[:10]
    
    # Preparar datos para mostrar en la tabla
    ventas_tabla = []
    for venta in ventas_recientes:
        # Obtener el primer producto de la venta como muestra
        primer_producto = venta.detalles.select_related('producto').first()
        producto_nombre = primer_producto.producto.nombre if primer_producto else "Múltiples productos"
        
        ventas_tabla.append({
            'id': venta.id,
            'cliente': f"{venta.cliente.nombres} {venta.cliente.apellidos}",
            'producto': producto_nombre,
            'fecha': venta.fecha,
            'monto': venta.total,
            'estado': venta.estado,
            'get_estado_display': venta.get_estado_display()
        })
    
    # Obtener productos con stock bajo
    productos_stock_bajo = Producto.objects.filter(
        activo=True,
        stock__lte=F('stock_minimo')
    ).order_by('stock')[:5]
    
    # Obtener últimos clientes registrados
    ultimos_clientes = Cliente.objects.filter(activo=True).order_by('-fecha_registro')[:5]
    
    context = {
        'stats': stats,
        'ventas_recientes': ventas_tabla,
        'productos_stock_bajo': productos_stock_bajo,
        'ultimos_clientes': ultimos_clientes,
        'now': timezone.now(),
    }
    
    return render(request, 'usuarios/dashboard_empleado.html', context)