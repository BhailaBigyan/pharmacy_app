from django.urls import path
from . import views

urlpatterns = [
    # Pharmacist Medicine Management
    
    path('medicine/list/', views.medicine_list, name='pharmacist_medicine_list'),
    path('medicine/detail/<int:medicine_id>/', views.medicine_detail, name='pharmacist_medicine_detail'),
    path('medicine/add/', views.medicine_add, name='pharmacist_medicine_add'),
    path('medicine/edit/<int:medicine_id>/', views.medicine_edit, name='pharmacist_medicine_edit'),
    path('medicine/delete/<int:medicine_id>/', views.medicine_delete, name='pharmacist_medicine_delete'),
    path('medicine/stock-report/', views.medicine_stock_report, name='pharmacist_medicine_stock_report'),
    path('medicine/low-stock/', views.medicine_low_stock, name='pharmacist_medicine_low_stock'),
    path('medicine/expired/', views.medicine_expired, name='pharmacist_medicine_expired'),
    path('medicine/expiring-soon/', views.medicine_expiring_soon, name='pharmacist_medicine_expiring_soon'),
]
