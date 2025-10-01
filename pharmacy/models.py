from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('pharmacist', 'Pharmacist'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username
