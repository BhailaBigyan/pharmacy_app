from django.db import models
<<<<<<< Updated upstream
from pytz import timezone
=======
from django.utils import timezone
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
    date = models.DateField(default=timezone('Asia/Kathmandu').localize)
=======
    date = models.DateField(default=timezone.now)
>>>>>>> Stashed changes
    created_at = models.DateTimeField(auto_now_add=True)
    received_by = models.CharField(max_length=150)

    def __str__(self):
<<<<<<< Updated upstream
        return f"{self.supplier.name} - {self.invoice_number}"
=======
        return f"{self.supplier.name} - {self.invoice_number}"


class SupplierInvoiceItem(models.Model):
    invoice = models.ForeignKey(SupplierInvoice, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey('medicine.Medicine', on_delete=models.CASCADE, related_name='supplier_invoice_items')
    batch_number = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity} @ {self.price}"
>>>>>>> Stashed changes
