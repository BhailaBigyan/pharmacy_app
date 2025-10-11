from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pharmacy.urls')),
    path('medicine/', include('medicine.urls')),
    path('supplier/', include('supplier.urls')),
    path('billing/', include('billing.urls')),
    path('pharmacist/', include('pharmacist.urls')),
]
