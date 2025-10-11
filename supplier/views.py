from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Supplier
from medicine.models import Medicine
# Create your views here.
from django.shortcuts import render, redirect
from .forms import SupplierForm
from .models import Supplier

def add_supplier(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_supplier')  # redirect after saving
    else:
        form = SupplierForm()
    
    return render(request, 'admin/supplier/add_supplier.html', {'form': form})

def supplier_detail(request, supplier_id):
    from datetime import date, timedelta
    
    supplier = get_object_or_404(Supplier, id=supplier_id)
    medicines = Medicine.objects.filter(supplier=supplier)
    today = date.today()
    expiring_soon_date = today + timedelta(days=30)
    
    return render(request, 'admin/supplier/supplier_detail.html', {
        'supplier': supplier,
        'medicines': medicines,
        'today': today,
        'expiring_soon_date': expiring_soon_date,
    })



def supplier_report(request):
    today = timezone.now().date()

    # Get supplier filter from GET parameter (e.g., ?supplier=1)
    supplier_id = request.GET.get('supplier')
    if supplier_id:
        medicines = Medicine.objects.filter(supplier_id=supplier_id).select_related('supplier')
    else:
        medicines = Medicine.objects.all().select_related('supplier')

    suppliers = Supplier.objects.all()

    context = {
        'medicines': medicines,
        'suppliers': suppliers,
        'selected_supplier': int(supplier_id) if supplier_id else None,
        'today': today
    }
    return render(request, 'admin/supplier/supplier_report.html', context)

def list_supplier(request):
    suppliers = Supplier.objects.all()
    return render(request, 'admin/supplier/list_supplier.html', {'suppliers': suppliers})

def edit_supplier(request, supplier_id):  # must accept supplier_id
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('list_supplier')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'admin/supplier/edit_supplier.html', {'form': form, 'supplier': supplier})

def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.delete()
    return redirect('list_supplier')
