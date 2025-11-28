"""
Public schema URL configuration for django-tenants.
This is used when accessing the public schema (no tenant).
"""
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect

from tenants import views as tenant_views


urlpatterns = [
    # Public landing page or tenant selection
    # path('', lambda request: redirect('landing_page'), name='public_home'),
    path('admin/', admin.site.urls),
path('tenants/', include(('tenants.urls', 'tenants'), namespace='tenants')),
    path('tenant-access/', tenant_views.tenant_access_view, name='tenant_access_public'),
    path('', include('pharmacy.urls')),
    path('medicine/', include(('medicine.urls', 'medicine'), namespace='medicine')),
    path('supplier/', include(('supplier.urls', 'supplier'), namespace='supplier')),
    path('billing/', include(('billing.urls', 'billing'), namespace='billing')),
    path('pharmacist/', include('pharmacist.urls')),
]

