from django.urls import path
from . import views


urlpatterns = [
    path('', views.bill, name='bill'),
    path('generate-invoice/', views.generate_invoice, name='generate_invoice'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('sales-report/', views.sales_report, name='sales_report'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('search-medicines/', views.search_medicines, name='search_medicines'),
]