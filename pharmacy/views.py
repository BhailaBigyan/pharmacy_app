from datetime import date
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from medicine.filters import MedicineFilter
from medicine.models import Medicine
# Create your views here.
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

# def login_view(request):
#     if request.method == "POST":
#         username = request.POST['username']
#         password = request.POST['password']
#         role = request.POST.get('role')  # 'admin' or 'staff'
#         user = authenticate(request, username=username, password=password)

#         if user is not None:
    
#             # if role is 'admin' redirect to admin dashboard if role is 'staff' redirect to staff dashboard
#             login(request, user)
#             return redirect('index')  # replace with your success page
#         else:
#             messages.error(request, "Invalid username or password")
#     return render(request, "login.html")
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)  # we need a custom backend if using custom User

        if user:
            login(request, user)
            # redirect based on role
            if user.role == 'admin':
                return redirect('index')
            elif user.role == 'pharmacist':
                return redirect('pharmacist_dashboard')
            else:
                return redirect('staff_dashboard')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "login.html")


from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def index(request):
    total_medicines = Medicine.objects.count()
    out_of_stock = Medicine.objects.filter(stock_qty__lte=0).count()
    expired_medicines = Medicine.objects.filter(exp_date__lt=timezone.now().date()).count()

    context = {
        'total_medicines': total_medicines,
        'out_of_stock': out_of_stock,
        'expired_medicines': expired_medicines,
    }
    return render(request, 'admin/dashboard.html', context)

#for stock report

def stock_report(request):
    medicines = Medicine.objects.all()
    return render(request, 'admin/stock/stock_report.html', {
        "medicines": medicines,
         "today": date.today(),
    })


from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# def register_view(request):
    # if request.method == "POST":
    #     form = UserCreationForm(request.POST)
    #     if form.is_valid():
    #         user = form.save()  # creates user in DB
    #         messages.success(request, "Account created successfully! Please log in.")
    #         return redirect("login")
    # else:
    #     form = UserCreationForm()
    # return render(request, "register.html", {"form": form})
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.contrib import messages

def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, "register.html", {"form": form})
