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
        
        # Primero intentamos encontrar al usuario por email
        try:
            user = User.objects.get(email=username_or_email)
            username = user.username
        except User.DoesNotExist:
            username = username_or_email
            
        # Intentamos la autenticación
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
    if request.user.es_administrador():
        return render(request, 'usuarios/inicio.html')
    elif request.user.es_empleado():
        return render(request, 'usuarios/dashboard_empleado.html')
    
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

# usuarios/views.py
@login_required
@rol_requerido(['Administrador'])
@require_http_methods(["POST"])
def crear_usuario(request):
    try:
        # Obtener los datos del cuerpo de la petición
        data = json.loads(request.body)
        
        # Crear el diccionario de datos para el formulario
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
            usuario.rol_id = form_data['rol']  # Asignar el rol directamente por ID
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
            # Devolver errores de validación específicos
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
    
    # Con PUT, los datos vienen en request.body como JSON
    try:
        datos = json.loads(request.body)
        username = datos.get('username')
        email = datos.get('email')
        rol_id = datos.get('rol_id')
        is_active = datos.get('is_active')
        
        # Validar datos únicos
        if UsuarioPersonalizado.objects.exclude(id=usuario_id).filter(username=username).exists():
            return JsonResponse({'error': 'El nombre de usuario ya existe'}, status=400)
        if UsuarioPersonalizado.objects.exclude(id=usuario_id).filter(email=email).exists():
            return JsonResponse({'error': 'El email ya existe'}, status=400)
        
        # Actualizar solo si los campos están presentes
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
