from django.shortcuts import render

# Create your views here.
def add_supplier(request):
    return render(request, 'supplier/add_supplier.html')

def supplier_report(request):
    return render(request, 'supplier/supplier_report.html')

def list_supplier(request):
    return render(request, 'supplier/list_supplier.html')

def edit_supplier(request, supplier_id):
    return render(request, 'supplier/edit_supplier.html', {'supplier_id': supplier_id})

def delete_supplier(request, supplier_id):
    return render(request, 'supplier/delete_supplier.html', {'supplier_id': supplier_id})