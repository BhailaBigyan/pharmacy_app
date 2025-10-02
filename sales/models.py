from django.db import models
from medicine.models import Medicine
from pharmacy.models import User  

class Sale(models.Model):
    sale_id = models.AutoField(primary_key=True)
    pharmacist = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'pharmacist'})
    date = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(max_length=100)
    

    def __str__(self):
        return f"Sale {self.sale_id} - {self.customer_name}"

    def total_amount(self):
        return sum(item.total_price() for item in self.items.all())

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.quantity * self.price
