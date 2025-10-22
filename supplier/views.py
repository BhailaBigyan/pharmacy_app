from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Sum
from datetime import datetime
import json

from .models import Supplier, SupplierInvoice, SupplierInvoiceItem
from medicine.models import Medicine
from .forms import SupplierForm

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
    supplier_invoices = SupplierInvoice.objects.all().select_related('supplier')
    return render(request, 'admin/supplier/list_supplier.html', {'suppliers': suppliers, 'supplier_invoices': supplier_invoices})

def view_supplier_invoice(request, invoice_id):
    invoice = get_object_or_404(SupplierInvoice, id=invoice_id)
    items = invoice.items.all()  # SupplierInvoiceItem related_name='items'
    return render(request, "admin/supplier/supplier_invoice_detail.html", {
        "invoice": invoice,
        "items": items,
    })

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

@login_required
def supplier_invoice_entry(request):
    suppliers = Supplier.objects.all()
    medicines = Medicine.objects.all()
    return render(request, 'admin/supplier/supplier_invoice_entry.html', {
        'suppliers': suppliers,
        'medicines': medicines,
    })

@login_required
def supplier_invoice_list(request):
    invoices = SupplierInvoice.objects.all().order_by('-created_at').select_related('supplier').prefetch_related('items')
    
    # Calculate total for each invoice
    for invoice in invoices:
        invoice.total_amount = invoice.items.aggregate(total=Sum('total'))['total'] or 0
    
    return render(request, 'admin/supplier/supplier_invoice_list.html', {
        'invoices': invoices,
    })

@login_required
def supplier_invoice_detail(request, invoice_id):
    invoice = get_object_or_404(SupplierInvoice, id=invoice_id)
    items = invoice.items.all().select_related('medicine')
    
    # Calculate total amount
    invoice.total_amount = invoice.items.aggregate(total=Sum('total'))['total'] or 0
    
    return render(request, 'admin/supplier/supplier_invoice_detail.html', {
        'invoice': invoice,
        'items': items,
    })

@csrf_exempt
def get_next_invoice_number(request):
    try:
        # Get the last invoice number
        last_invoice = SupplierInvoice.objects.order_by('-id').first()
        if last_invoice and last_invoice.invoice_number:
            # Extract number from last invoice (assuming format like SUP-00001)
            import re
            match = re.search(r'(\d+)', last_invoice.invoice_number)
            if match:
                next_num = int(match.group(1)) + 1
            else:
                next_num = 1
        else:
            next_num = 1
        
        invoice_number = f"SUP-{next_num:05d}"
        return JsonResponse({'success': True, 'invoice_number': invoice_number})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_medicine_api(request, med_id):
    try:
        medicine = Medicine.objects.get(medicine_id=med_id)
        return JsonResponse({
            'success': True,
            'medicine': {
                'id': medicine.medicine_id,
                'name': medicine.name,
                'brand_name': medicine.brand_name,
                'price': str(medicine.price),
                'stock_qty': medicine.stock_qty,
                'batch_number': medicine.batch_number or '',
            }
        })
    except Medicine.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Medicine not found'})

@csrf_exempt
def create_supplier_invoice(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            supplier_id = data.get('supplierId')
            invoice_number = data.get('invoiceNumber')
            received_by = data.get('receivedBy', 'system')
            date_str = data.get('date')
            invoice_date = None
            if date_str:
                try:
                    invoice_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except Exception:
                    invoice_date = timezone.now().date()
            else:
                invoice_date = timezone.now().date()
            items = data.get('items', [])

            with transaction.atomic():
                supplier = Supplier.objects.get(id=supplier_id)
                invoice = SupplierInvoice.objects.create(
                    supplier=supplier,
                    invoice_number=invoice_number,
                    date=invoice_date,
                    received_by=received_by,
                )

                # Loop through items
                for item in items:
                    quantity = int(item.get('quantity', 0))
                    price = float(item.get('price', 0))
                    batch_number = item.get('batchNumber')
                    
                    med_id = item.get('medicineId')
                    new_medicine_name = item.get('newMedicineName')
                    new_brand_name = item.get('newBrandName')
                    
                    med = None
                    
                    if med_id:
                        # Existing medicine
                        try:
                            med = Medicine.objects.get(medicine_id=med_id)
                            # Update stock and price
                            med.stock_qty += quantity
                            med.price = price
                            med.batch_number = batch_number or med.batch_number
                            med.supplier = supplier
                            med.save()
                        except Medicine.DoesNotExist:
                            return JsonResponse({'success': False, 'error': f'Medicine with ID {med_id} not found'})
                    elif new_medicine_name:
                        # New medicine
                        med = Medicine.objects.create(
                            name=new_medicine_name,
                            brand_name=new_brand_name or '',
                            price=price,
                            stock_qty=quantity,
                            supplier=supplier,
                            batch_number=batch_number,
                            mfg_date=timezone.now().date(),
                            exp_date=timezone.now().date() + timezone.timedelta(days=365),  # default 1 year
                            category='tablet/capsule',  # default category
                        )
                    else:
                        return JsonResponse({'success': False, 'error': 'Either medicine ID or new medicine name required'})

                    SupplierInvoiceItem.objects.create(
                        invoice=invoice,
                        medicine=med,
                        batch_number=batch_number,
                        quantity=quantity,
                        price=price,
                        total=price * quantity,
                    )

            return JsonResponse({'success': True, 'message': 'Invoice saved and stock updated!', 'invoice_id': invoice.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})