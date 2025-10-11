from django.urls import path
from . import user_management

urlpatterns = [
    # User Management
    path('users/', user_management.user_list, name='user_list'),
    path('users/detail/<int:user_id>/', user_management.user_detail, name='user_detail'),
    path('users/add/', user_management.user_add, name='user_add'),
    path('users/edit/<int:user_id>/', user_management.user_edit, name='user_edit'),
    path('users/delete/<int:user_id>/', user_management.user_delete, name='user_delete'),
    path('users/activate/<int:user_id>/', user_management.user_activate, name='user_activate'),
    path('users/deactivate/<int:user_id>/', user_management.user_deactivate, name='user_deactivate'),
]
