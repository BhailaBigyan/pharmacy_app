from django.db import models

# Create your models here.
from django.db import models

class Supplier(models.Model):
    id = models.AutoField(primary_key=True)   # auto increment id
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.name
