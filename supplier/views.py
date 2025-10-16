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
    for med in medicines:
        med.total_value = med.price * med.stock_qty

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


# supplier/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Supplier, SupplierInvoice
from medicine.models import Medicine
import json

@login_required
def supplier_invoice_entry(request):
    suppliers = Supplier.objects.all()
    medicines = Medicine.objects.all()
    return render(request, 'admin/supplier/supplier_invoice_entry.html', {
        'suppliers': suppliers,
        'medicines': medicines,
    })
# supplier/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from supplier.models import Supplier
from medicine.models import Medicine
from django.utils import timezone
from django.db import transaction

@csrf_exempt
def create_supplier_invoice(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            supplier_id = data.get('supplierId')
            invoice_number = data.get('invoiceNumber')
            items = data.get('items', [])

            supplier = Supplier.objects.get(id=supplier_id)

            with transaction.atomic():
                # Loop through items
                for item in items:
                    med_id = item.get('id')
                    name = item.get('name', None)  # optional, if you pass name for new medicine
                    brand_name = item.get('brand_name', '')  # optional
                    quantity = int(item.get('quantity', 0))
                    price = float(item.get('price', 0))

                    if med_id:  
                        # Existing medicine → update stock and price
                        med = Medicine.objects.get(id=med_id)
                        med.stock_qty += quantity
                        med.price = price
                        med.save()
                    else:
                        # New medicine → create
                        med = Medicine.objects.create(
                            name=name,
                            brand_name=brand_name,
                            price=price,
                            stock_qty=quantity,
                            supplier=supplier,
                            mfg_date=timezone.now().date(),
                            exp_date=timezone.now().date() + timezone.timedelta(days=365),  # default 1 year
                        )

            return JsonResponse({'success': True, 'message': 'Invoice saved and stock updated!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
