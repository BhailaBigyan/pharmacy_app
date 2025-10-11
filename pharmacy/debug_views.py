from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .decorators import admin_required

@login_required
def debug_user_info(request):
    """Debug view to check user information"""
    user = request.user
    return render(request, 'debug_user.html', {
        'username': user.username,
        'role': user.role,
        'is_authenticated': user.is_authenticated,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'is_active': user.is_active,
    })

@admin_required
def debug_admin_test(request):
    """Debug view to test admin authorization"""
    return render(request, 'debug_admin.html', {
        'message': 'Admin access successful!',
        'user': request.user.username,
    })
