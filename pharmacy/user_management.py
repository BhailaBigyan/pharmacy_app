from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .decorators import admin_required
from .forms import UserForm, UserEditForm

User = get_user_model()

@admin_required
def user_list(request):
    """List all users for admin"""
    users = User.objects.all().order_by('-date_joined')
    
    # Pagination
    paginator = Paginator(users, 20)  # 20 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin/users/user_list.html', {
        'page_obj': page_obj,
    })

@admin_required
def user_detail(request, user_id):
    """View user details for admin"""
    user = get_object_or_404(User, id=user_id)
    
    return render(request, 'admin/users/user_detail.html', {
        'user_obj': user,
    })

@admin_required
def user_add(request):
    """Add new user for admin"""
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'User created successfully!')
            return redirect('user_list')
    else:
        form = UserForm()
    
    return render(request, 'admin/users/user_add.html', {
        'form': form,
    })

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .forms import UserEditForm
@admin_required

def user_edit(request, user_id):
    """Edit user for admin"""
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if password and password != '********':
                user.set_password(password)
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('user_detail', user_id=user.id)
    else:
        form = UserEditForm(instance=user)

    return render(request, 'admin/users/user_edit.html', {
        'form': form,
        'user_obj': user,
    })


@admin_required
def user_delete(request, user_id):
    """Delete user for admin"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" deleted successfully!')
        return redirect('user_list')
    
    return render(request, 'admin/users/user_delete.html', {
        'user_obj': user,
    })

@admin_required
def user_activate(request, user_id):
    """Activate user account"""
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f'User "{user.username}" activated successfully!')
    return redirect('user_detail', user_id=user.id)

@admin_required
def user_deactivate(request, user_id):
    """Deactivate user account"""
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f'User "{user.username}" deactivated successfully!')
    return redirect('user_detail', user_id=user.id)
