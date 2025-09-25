from django import forms
from .models import Medicine

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name',
            'description',
            'company',
            'price',
            'stock',
            'mfg_date',
            'exp_date',
            'supplier',
        ]
        widgets = {
            'mfg_date': forms.DateInput(attrs={'type': 'date'}),
            'exp_date': forms.DateInput(attrs={'type': 'date'}),
        }
