from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    """
    Decorator to check if user has required role
    Usage: @role_required(['admin']) or @role_required(['pharmacist', 'staff'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('login')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def admin_required(view_func):
    """Decorator to require admin role"""
    return role_required(['admin'])(view_func)

def pharmacist_required(view_func):
    """Decorator to require pharmacist role"""
    return role_required(['pharmacist'])(view_func)

def staff_required(view_func):
    """Decorator to require staff role"""
    return role_required(['staff'])(view_func)

def pharmacist_or_staff_required(view_func):
    """Decorator to require pharmacist or staff role"""
    return role_required(['pharmacist', 'staff'])(view_func)

def admin_or_pharmacist_required(view_func):
    """Decorator to require admin or pharmacist role"""
    return role_required(['admin', 'pharmacist'])(view_func)
