from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('add_supplier/', views.add_supplier, name='add_supplier'),
    path('supplier_report/', views.supplier_report, name='supplier_report'),
    path('list_supplier/', views.list_supplier, name='list_supplier'),
    path('edit_supplier/', views.edit_supplier, name='edit_supplier'),
    path('delete_supplier/<int:supplier_id>/', views.delete_supplier, name='delete_supplier')
]