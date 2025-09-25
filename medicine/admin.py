from django.contrib import admin
from .models import Medicine
# Register your models here.

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'stock')
    search_fields = ('name', 'description')
    list_filter = ('company', 'supplier', 'mfg_date', 'exp_date')
    ordering = ('name',)