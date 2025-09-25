from django.shortcuts import redirect, render

from medicine.filters import MedicineFilter
from medicine.forms import MedicineForm
from .models import Medicine

# Create your views here.

def search(request):
    return render(request, 'admin/search_medicine.html')


def add_medicine(request):
    if request.method == "POST":
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_medicine')  # redirect to medicine list after saving
    else:
        form = MedicineForm()
    return render(request, "admin/medicine/add_medicine.html", {"form": form})

# def list_medicine(request):
#     medicines = Medicine.objects.all()
#     medicine_filter = MedicineFilter(request.GET, queryset=medicines)
#     return render(request, 'admin/medicine/list_medicine.html', {"medicines": medicines, "filter": medicine_filter})

def list_medicine(request):
    medicines = Medicine.objects.all()
    medicine_filter = MedicineFilter(request.GET, queryset=medicines)
    return render(request, 'admin/medicine/list_medicine.html', {
        "medicines": medicines,
        "filter": medicine_filter
    })


def delete_medicine(request, pk):
    medicine = Medicine.objects.get(id=pk)
    if request.method == "POST":
        medicine.delete()
        return redirect('list_medicine')
    return render(request, 'admin/medicine/delete_medicine.html', {'medicine': medicine})

def update_medicine(request, pk):
    medicine = Medicine.objects.get(id=pk)
    if request.method == "POST":
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            return redirect('list_medicine')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'admin/medicine/update_medicine.html', {'form': form})   