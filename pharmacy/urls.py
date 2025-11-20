from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect
from . import views
from . import user_urls

urlpatterns = [
    path('', views.index, name='index'),
    path('notifications/', views.notifications, name='notifications'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.company_register, name='company_register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    #For stock
    path('stock/stock_report/', views.stock_report, name='stock_report'),
    path('pharmacist/dashboard/', views.pharmacist_dashboard, name='pharmacist_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    # User Management
    path('user-management/', include(user_urls)),
    # Redirect old admin URL to new user management URL
    path('admin/users/', lambda request: redirect('user_list'), name='admin_users_redirect'),
  
  ]
