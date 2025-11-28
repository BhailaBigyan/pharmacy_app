from django.urls import path
from . import views

app_name = 'tenants'

urlpatterns = [
    path('create-tenant/', views.create_tenant_view, name='create_tenant'),
    path('access/', views.tenant_access_view, name='tenant_access'),
]

