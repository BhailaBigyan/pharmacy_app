from django.db import models

# Create your models here.

class Medicine(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    company = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    mfg_date = models.DateField()
    exp_date = models.DateField()
    supplier = models.CharField(max_length=100)

    def __str__(self):
        return self.name