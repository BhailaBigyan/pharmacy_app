from django.db import models
from pytz import timezone

class Supplier(models.Model):
    id = models.AutoField(primary_key=True)   # auto increment id
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.name


class SupplierInvoice(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=100, unique=True)
    date = models.DateField(default=timezone('Asia/Kathmandu').localize)
    created_at = models.DateTimeField(auto_now_add=True)
    received_by = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.supplier.name} - {self.invoice_number}"