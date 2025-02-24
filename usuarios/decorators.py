from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def rol_requerido(roles_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.rol or request.user.rol.nombre not in roles_permitidos:
                messages.error(request, 'No tienes permiso para acceder a esta página.')
                return redirect('inicio')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator