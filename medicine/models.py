from django.db import models
from supplier.models import Supplier   # link with Supplier app


class Medicine(models.Model):
    medicine_id = models.AutoField(primary_key=True)   # custom PK
    name = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=100)
    batch_number = models.CharField(max_length=50, null=True, blank=True)
    
    CATEGORY_CHOICES = [
        ("tablet/capsule", "Tablet/Capsule"),
        ("liquid", "Liquid"),
        ("patch", "Patch"),
        ("dose form", "Dose Form"),
        ("ointment", "Ointment"),
        ("syrup", "Syrup"),
        ("injection", "Injection"),
        ("cream", "Topical Cream"),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="tablet/capsule")
    
    mfg_date = models.DateField()
    exp_date = models.DateField()
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_qty = models.PositiveIntegerField(default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="medicines")

    def __str__(self):
        return f"{self.name} ({self.brand_name})"
    

    def total_price(self):
        return self.price * self.stock_qty