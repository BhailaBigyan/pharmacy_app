from django.db import models
from django.utils import timezone

class Supplier(models.Model):
    id = models.AutoField(primary_key=True)   # auto increment id
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, null=True, blank=True)
    address = models.TextField()
    pan_number = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name


class SupplierInvoice(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=100, unique=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    received_by = models.CharField(max_length=150, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    def __str__(self):
        return f"{self.supplier.name} - {self.invoice_number}"
    
class SupplierInvoiceItem(models.Model):
    invoice = models.ForeignKey(SupplierInvoice, on_delete=models.CASCADE, related_name='items')
    medicine_name = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=100)
    batch_number = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    mfg_date = models.DateField()
    exp_date = models.DateField()
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.medicine_name} ({self.brand_name}) - {self.quantity} @ {self.price}"