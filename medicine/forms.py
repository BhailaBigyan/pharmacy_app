from django import forms
from .models import Medicine

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name',
            'brand_name',
            'batch_number',
            'category',
            'mfg_date',
            'exp_date',
            'price',
            'stock_qty',
            'supplier',
        ]
        widgets = {
            'mfg_date': forms.DateInput(attrs={'type': 'date'}),
            'exp_date': forms.DateInput(attrs={'type': 'date'}),
        }
