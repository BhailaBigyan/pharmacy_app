from django.urls import path
from . import views

urlpatterns = [
    path('add_supplier/', views.add_supplier, name='add_supplier'),
    path('supplier_detail/<int:supplier_id>/', views.supplier_detail, name='supplier_detail'),
    path('edit_supplier/<int:supplier_id>/', views.edit_supplier, name='edit_supplier'),
    path('delete_supplier/<int:supplier_id>/', views.delete_supplier, name='delete_supplier'),
    path('list_supplier/', views.list_supplier, name='list_supplier'),
    path('supplier_report/', views.supplier_report, name='supplier_report'),
    path('supplier_invoice/', views.supplier_invoice_entry, name='supplier_invoice'),
    path('supplier_invoice_list/', views.supplier_invoice_list, name='supplier_invoice_list'),
    path('supplier_invoice_detail/<int:invoice_id>/', views.supplier_invoice_detail, name='supplier_invoice_detail'),
    path('create_supplier_invoice/', views.create_supplier_invoice, name='create_supplier_invoice'),
    path('api/medicine/<int:med_id>/', views.get_medicine_api, name='get_medicine_api'),
    path('api/next-invoice-number/', views.get_next_invoice_number, name='get_next_invoice_number'),
    path('view_supplier_invoice/<int:invoice_id>/', views.view_supplier_invoice, name='view_supplier_invoice'),
]
