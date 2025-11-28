from datetime import date
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages

from medicine.filters import MedicineFilter
from medicine.forms import MedicineForm
from .models import Medicine

# Add Medicine
def add_medicine(request):
    if request.method == "POST":
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('medicine:list_medicine')
    else:
        form = MedicineForm()
    return render(request, "admin/medicine/add_medicine.html", {"form": form})

# List Medicines
def list_medicine(request):
    medicines = Medicine.objects.all()
    medicine_filter = MedicineFilter(request.GET, queryset=medicines)
    return render(request, 'admin/medicine/list_medicine.html', {
        "filter": medicine_filter,
        "today": date.today(),
    })

# Medicine Detail
def medicine_detail(request, medicine_id):
    from datetime import timedelta
    
    medicine = get_object_or_404(Medicine, medicine_id=medicine_id)
    today = date.today()
    expiring_soon_date = today + timedelta(days=30)
    
    return render(request, 'admin/medicine/medicine_detail.html', {
        'medicine': medicine,
        'today': today,
        'expiring_soon_date': expiring_soon_date,
    })

# Delete Medicine
def delete_medicine(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == "POST":
        medicine.delete()
        return redirect('medicine:list_medicine')
    return render(request, 'admin/medicine/delete_medicine.html', {'medicine': medicine})

# Update Medicine
def update_medicine(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == "POST":
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            return redirect('medicine:list_medicine')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'admin/medicine/update_medicine.html', {'form': form})

# Edit Page Medicine (if needed as a separate view)
def edit_page_medicine(request, medicine_id):
    medicine = get_object_or_404(Medicine, medicine_id=medicine_id)
    
    if request.method == "POST":
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine updated successfully!')
            return redirect('medicine_detail', medicine_id=medicine.medicine_id)
    else:
        form = MedicineForm(instance=medicine)
    
    return render(request, 'admin/medicine/edit_page_medicine.html', {
        'form': form,
        'medicine': medicine,
        'today': date.today(),
    })

# Expired Medicines
def expired_medicines(request):
    today = date.today()
    expired_list = Medicine.objects.filter(exp_date__lt=today).order_by('exp_date')
    return render(request, 'admin/dashboard/expired_medicine.html', {
        'expired_list': expired_list,
        'today': today
    })

# Stock Out Medicines
def stock_out_medicines(request):
    out_of_stock_list = Medicine.objects.filter(stock_qty__lte=0).order_by('name')
    return render(request, 'admin/dashboard/stockout_medicine.html', {
        'out_of_stock_list': out_of_stock_list
    })
