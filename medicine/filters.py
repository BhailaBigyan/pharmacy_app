import django_filters
from .models import Medicine

class MedicineFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(lookup_expr='icontains')
    batch_number = django_filters.CharFilter(lookup_expr='icontains')
    

    class Meta:
        model = Medicine
        fields = ['name', 'batch_number', 'category']
        
class StockFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(lookup_expr='icontains')
    batch_number = django_filters.CharFilter(lookup_expr='icontains')
    

    class Meta:
        model = Medicine
        fields = [ 'batch_number', 'category']
