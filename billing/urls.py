from django.urls import path
from . import views

urlpatterns = [
    path('', views.bill, name='bill'),
    path('generate-invoice/', views.generate_invoice, name='generate_invoice'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('sales-report/', views.sales_report, name='sales_report'),
]
