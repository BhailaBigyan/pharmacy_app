from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('pharmacist', 'Pharmacist'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    reset_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username

class Company(models.Model):
    company_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    pan_number = models.CharField(max_length=50, blank=True, null=True)
    vat_number = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.company_name