from django.contrib import admin
from .models import Medicine

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = (
        'medicine_id',
        'name',
        'brand_name',
        'category',
      # make sure this exists in your model
        'price',
        'stock_qty',
        'mfg_date',
        'exp_date',
        'supplier',  # ForeignKey works fine
    )
    search_fields = ('name', 'brand_name', 'category',)
    list_filter = ('supplier', 'category', 'mfg_date', 'exp_date')
    ordering = ('name',)
