from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import date, timedelta
from pharmacy.decorators import pharmacist_or_staff_required
from medicine.models import Medicine
from medicine.forms import MedicineForm
from medicine.filters import MedicineFilter

# Pharmacist Medicine Views
@pharmacist_or_staff_required
def medicine_list(request):
    """List all medicines for pharmacists"""
    medicines = Medicine.objects.all().order_by('name')
    medicine_filter = MedicineFilter(request.GET, queryset=medicines)
    
    # Pagination
    paginator = Paginator(medicine_filter.qs, 20)  # 20 medicines per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pharmacist/medicine/medicine_list.html', {
        'filter': medicine_filter,
        'page_obj': page_obj,
        'today': date.today(),
    })

@pharmacist_or_staff_required
def medicine_detail(request, medicine_id):
    """View medicine details for pharmacists"""
    medicine = get_object_or_404(Medicine, medicine_id=medicine_id)
    today = date.today()
    expiring_soon_date = today + timedelta(days=30)
    
    return render(request, 'pharmacist/medicine/medicine_detail.html', {
        'medicine': medicine,
        'today': today,
        'expiring_soon_date': expiring_soon_date,
    })

@pharmacist_or_staff_required
def medicine_add(request):
    """Add new medicine for pharmacists"""
    if request.method == "POST":
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine added successfully!')
            return redirect('pharmacist_medicine_list')
    else:
        form = MedicineForm()
    
    return render(request, 'pharmacist/medicine/medicine_add.html', {
        'form': form,
    })

@pharmacist_or_staff_required
def medicine_edit(request, medicine_id):
    """Edit medicine for pharmacists"""
    medicine = get_object_or_404(Medicine, medicine_id=medicine_id)
    
    if request.method == "POST":
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine updated successfully!')
            return redirect('pharmacist_medicine_detail', medicine_id=medicine.medicine_id)
    else:
        form = MedicineForm(instance=medicine)
    
    return render(request, 'pharmacist/medicine/medicine_edit.html', {
        'form': form,
        'medicine': medicine,
    })

@pharmacist_or_staff_required
def medicine_delete(request, medicine_id):
    """Delete medicine for pharmacists"""
    medicine = get_object_or_404(Medicine, medicine_id=medicine_id)
    
    if request.method == "POST":
        medicine_name = medicine.name
        medicine.delete()
        messages.success(request, f'Medicine "{medicine_name}" deleted successfully!')
        return redirect('pharmacist_medicine_list')
    
    return render(request, 'pharmacist/medicine/medicine_delete.html', {
        'medicine': medicine,
    })

@pharmacist_or_staff_required
def medicine_stock_report(request):
    """Stock report for pharmacists"""
    from datetime import timedelta
    
    medicines = Medicine.objects.all().order_by('name')
    today = date.today()
    expiring_soon_date = today + timedelta(days=30)
    
    # Calculate statistics
    total_medicines = medicines.count()
    in_stock = medicines.filter(stock_qty__gt=10).count()
    low_stock = medicines.filter(stock_qty__lte=10, stock_qty__gt=0).count()
    out_of_stock = medicines.filter(stock_qty__lte=0).count()
    expired = medicines.filter(exp_date__lt=today).count()
    expiring_soon = medicines.filter(exp_date__lte=expiring_soon_date, exp_date__gte=today).count()
    
    return render(request, 'pharmacist/medicine/medicine_stock_report.html', {
        'medicines': medicines,
        'today': today,
        'expiring_soon_date': expiring_soon_date,
        'total_medicines': total_medicines,
        'in_stock': in_stock,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'expired': expired,
        'expiring_soon': expiring_soon,
    })

@pharmacist_or_staff_required
def medicine_low_stock(request):
    """View low stock medicines"""
    medicines = Medicine.objects.filter(stock_qty__lte=10, stock_qty__gt=0).order_by('stock_qty')
    
    return render(request, 'pharmacist/medicine/medicine_low_stock.html', {
        'medicines': medicines,
        'today': date.today(),
    })

@pharmacist_or_staff_required
def medicine_expired(request):
    """View expired medicines"""
    medicines = Medicine.objects.filter(exp_date__lt=date.today()).order_by('exp_date')
    
    return render(request, 'pharmacist/medicine/medicine_expired.html', {
        'medicines': medicines,
        'today': date.today(),
    })

@pharmacist_or_staff_required
def medicine_expiring_soon(request):
    """View medicines expiring soon"""
    from datetime import timedelta
    
    today = date.today()
    expiring_soon_date = today + timedelta(days=30)
    medicines = Medicine.objects.filter(
        exp_date__lte=expiring_soon_date, 
        exp_date__gte=today
    ).order_by('exp_date')
    
    return render(request, 'pharmacist/medicine/medicine_expiring_soon.html', {
        'medicines': medicines,
        'today': today,
        'expiring_soon_date': expiring_soon_date,
    })
