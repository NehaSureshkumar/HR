from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not request.user.is_staff and 'ADMIN' in roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard')
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator 