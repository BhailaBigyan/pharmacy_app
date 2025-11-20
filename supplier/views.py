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


from django.shortcuts import get_object_or_404, render
from .models import SupplierInvoice
def list_supplier(request):
    suppliers = Supplier.objects.all()
    supplier_invoices = SupplierInvoice.objects.all().select_related('supplier')
    return render(request, 'admin/supplier/list_supplier.html', {'suppliers': suppliers, 'supplier_invoices': supplier_invoices})

def view_supplier_invoice(request, invoice_id):
    invoice = get_object_or_404(SupplierInvoice, id=invoice_id)
    items = invoice.items.all()  # SupplierInvoiceItem related_name='items'
    return render(request, "admin/supplier/supplier_invoice_detail.html", {
        "invoice": invoice,
        "items": items,
    })

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
from .models import SupplierInvoice, SupplierInvoiceItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from .models import Supplier, SupplierInvoice, SupplierInvoiceItem
from medicine.models import Medicine

@csrf_exempt
def create_supplier_invoice(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"})

    # 1️⃣ Get supplier
    try:
        supplier = Supplier.objects.get(id=data.get("supplierId"))
    except Supplier.DoesNotExist:
        return JsonResponse({"error": "Supplier not found"})

    # 2️⃣ Create a new invoice
    invoice = SupplierInvoice.objects.create(
        supplier=supplier,
        invoice_number=data.get("invoiceNumber") or f"AUTO-{timezone.now().strftime('%Y%m%d%H%M%S')}",
        date=timezone.now().date(),
        received_by=request.user.username if request.user.is_authenticated else "System",
    )

    total = 0
    items = data.get("items", [])

    for item in items:
        name = item.get("name")
        brand_name = item.get("brand_name")
        batch_number = item.get("batch_number")
        category = item.get("category")
        mfg_date = item.get("mfg_date")
        exp_date = item.get("exp_date")
        quantity = int(item.get("quantity") or 0)
        price = float(item.get("price") or 0)
        total += quantity * price

        # 3️⃣ Save SupplierInvoiceItem
        SupplierInvoiceItem.objects.create(
            invoice=invoice,
            medicine_name=name,
            brand_name=brand_name,
            batch_number=batch_number or "N/A",
            category=category,
            mfg_date=mfg_date,
            exp_date=exp_date,
            quantity=quantity,
            price=price,
            
        )

        # 4️⃣ Save / update Medicine stock
        medicine, created = Medicine.objects.get_or_create(
            name=name,
            brand_name=brand_name,
            batch_number=batch_number,
            supplier=supplier,
            defaults={
                "category": category,
                "mfg_date": mfg_date,
                "exp_date": exp_date,
                "price": price,
                "stock_qty": quantity,
            }
        )
        if not created:
            # Update existing medicine stock and info
            medicine.stock_qty += quantity
            medicine.category = category
            medicine.mfg_date = mfg_date
            medicine.exp_date = exp_date
            medicine.price = price
            medicine.save()

    invoice.total_amount = total
    invoice.save()

    return JsonResponse({"invoice_id": invoice.id})
