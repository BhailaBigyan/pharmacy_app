from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('search_medicine/', views.search, name='search'),
    path('add_medicine/', views.add_medicine, name='add_medicine'),
    path('list_medicine/', views.list_medicine, name='list_medicine'),
    path('edit_page_medicine/', views.edit_page_medicine, name='edit_page_medicine'),
    path('delete_medicine/<int:pk>/', views.delete_medicine, name='delete_medicine'),
    path('update_medicine/<int:pk>/', views.update_medicine, name='update_medicine'),
    path('expired/', views.expired_medicines, name='expired_medicines'),
    path('stock_out/', views.stock_out_medicines, name='stock_out_medicines'),


  ]
