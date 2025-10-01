import django_filters
from .models import Medicine

class MedicineFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(lookup_expr='icontains')
    

    class Meta:
        model = Medicine
        fields = ['name', 'category']
