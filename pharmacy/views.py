from datetime import date
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from medicine.filters import MedicineFilter
from medicine.models import Medicine
# Create your views here.
from django.contrib.auth.decorators import login_required
from .decorators import admin_required, pharmacist_required, staff_required, pharmacist_or_staff_required

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
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
import string

def logout_view(request):
    logout(request)
    return redirect('login')

# Forgot Password Views
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate reset token
            reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            user.reset_token = reset_token
            user.save()
            
            # For testing purposes, we'll show the reset link instead of sending email
            reset_url = request.build_absolute_uri(f'/reset-password/{reset_token}/')
            
            messages.success(request, f'Password reset link generated! For testing: {reset_url}')
            return redirect('forgot_password')
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
    
    return render(request, 'forgot_password.html')

def reset_password(request, token):
    try:
        user = User.objects.get(reset_token=token)
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if password == confirm_password:
                user.set_password(password)
                user.reset_token = None
                user.save()
                messages.success(request, 'Password has been reset successfully. Please login.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
    except User.DoesNotExist:
        messages.error(request, 'Invalid reset token.')
        return redirect('login')
    
    return render(request, 'reset_password.html', {'token': token})

def test_forgot_password(request):
    """Test view for forgot password functionality"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate reset token
            reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            user.reset_token = reset_token
            user.save()
            
            # For testing purposes, we'll show the reset link instead of sending email
            reset_url = request.build_absolute_uri(f'/reset-password/{reset_token}/')
            
            messages.success(request, f'Password reset link generated! For testing: {reset_url}')
            return redirect('test_forgot_password')
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
    
    return render(request, 'test_forgot_password.html')


@admin_required
def index(request):
    # Redirect based on user role
    if request.user.role == 'admin':
        from datetime import timedelta

        total_medicines = Medicine.objects.count()
        out_of_stock = Medicine.objects.filter(stock_qty__lte=0).count()
        expired_medicines = Medicine.objects.filter(exp_date__lt=timezone.now().date()).count()

        today = timezone.now().date()
        three_days_from_now = today + timedelta(days=3)

        # Medicines expiring within next 3 days (but not already expired)
        expiring_in_3_days = Medicine.objects.filter(
            exp_date__gt=today,
            exp_date__lte=three_days_from_now
        ).order_by('exp_date')

        # Low stock threshold set to 10 units (includes >0 to exclude out of stock)
        low_stock_qs = Medicine.objects.filter(stock_qty__gt=0, stock_qty__lte=10).order_by('stock_qty', 'name')

        context = {
            'total_medicines': total_medicines,
            'out_of_stock': out_of_stock,
            'expired_medicines': expired_medicines,
            'expiring_in_3_days_count': expiring_in_3_days.count(),
            'expiring_in_3_days_list': expiring_in_3_days[:5],  # show first 5
            'low_stock_count': low_stock_qs.count(),
            'low_stock_list': low_stock_qs[:5],  # show first 5
        }
        return render(request, 'admin/dashboard.html', context)
    elif request.user.role == 'pharmacist':
        return redirect('pharmacist_dashboard')
    else:
        return redirect('staff_dashboard')

#for stock report

def stock_report(request):
    from datetime import timedelta
    
    medicines = Medicine.objects.all()
    today = date.today()
    expiring_soon_date = today + timedelta(days=30)
    
    # Calculate statistics
    total_medicines = medicines.count()
    in_stock = medicines.filter(stock_qty__gt=10).count()
    low_stock = medicines.filter(stock_qty__lte=10, stock_qty__gt=0).count()
    out_of_stock = medicines.filter(stock_qty__lte=0).count()
    
    return render(request, 'admin/stock/stock_report.html', {
        "medicines": medicines,
        "today": today,
        "expiring_soon_date": expiring_soon_date,
        "total_medicines": total_medicines,
        "in_stock": in_stock,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
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




# For pharmacist dashboard
@pharmacist_or_staff_required
def pharmacist_dashboard(request):
    from billing.models import Invoice, InvoiceItem
    from django.db.models import Sum, Count
    from datetime import datetime, timedelta
    
    # Basic medicine stats
    total_medicines = Medicine.objects.count()
    out_of_stock = Medicine.objects.filter(stock_qty__lte=0).count()
    expired_medicines = Medicine.objects.filter(exp_date__lt=timezone.now().date()).count()
    
    # Sales analytics
    today = timezone.now().date()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    # Today's sales
    today_sales = Invoice.objects.filter(created_at__date=today).aggregate(
        total=Sum('total'), count=Count('invoice_id')
    )
    
    # This month's sales
    month_sales = Invoice.objects.filter(created_at__date__gte=this_month).aggregate(
        total=Sum('total'), count=Count('invoice_id')
    )
    
    # Last month's sales
    last_month_sales = Invoice.objects.filter(
        created_at__date__gte=last_month,
        created_at__date__lt=this_month
    ).aggregate(total=Sum('total'), count=Count('invoice_id'))
    
    # Top selling medicines
    top_medicines = InvoiceItem.objects.values('medicine__name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('total')
    ).order_by('-total_sold')[:5]
    
    # Recent transactions
    recent_transactions = Invoice.objects.all().order_by('-created_at')[:5]
    
    # Sales trend (last 7 days)
    sales_trend = []
    for i in range(7):
        date = today - timedelta(days=i)
        daily_sales = Invoice.objects.filter(created_at__date=date).aggregate(
            total=Sum('total')
        )['total'] or 0
        sales_trend.append({
            'date': date.strftime('%m/%d'),
            'amount': float(daily_sales)
        })
    sales_trend.reverse()
    
    # Convert to JSON string for JavaScript
    import json
    sales_trend_json = json.dumps(sales_trend)

    context = {
        'total_medicines': total_medicines,
        'out_of_stock': out_of_stock,
        'expired_medicines': expired_medicines,
        'today_sales': today_sales['total'] or 0,
        'today_transactions': today_sales['count'] or 0,
        'month_sales': month_sales['total'] or 0,
        'month_transactions': month_sales['count'] or 0,
        'last_month_sales': last_month_sales['total'] or 0,
        'top_medicines': top_medicines,
        'recent_transactions': recent_transactions,
        'sales_trend': sales_trend_json,
    }
    return render(request, 'pharmacist/dashboard.html', context)

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime, timedelta
from datetime import timedelta, datetime
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from medicine.models import Medicine  # adjust to your app name




def admin_notifications(request):
    today = timezone.now().date()
    three_days_from_now = today + timedelta(days=3)

    # Query relevant data
    expiring_in_3_days = Medicine.objects.filter(
        exp_date__gt=today,
        exp_date__lte=three_days_from_now
    ).order_by('exp_date')

    low_stock_qs = Medicine.objects.filter(stock_qty__gt=0, stock_qty__lte=10).order_by('stock_qty', 'name')
    out_of_stock_qs = Medicine.objects.filter(stock_qty__lte=0).order_by('name')
    expired_qs = Medicine.objects.filter(exp_date__lt=today).order_by('exp_date')

    context = {
        'today': today,
        'expiring_in_3_days': expiring_in_3_days,
        'expiring_in_3_days_count': expiring_in_3_days.count(),
        'low_stock_list': low_stock_qs,
        'low_stock_count': low_stock_qs.count(),
        'out_of_stock_list': out_of_stock_qs,
        'out_of_stock_count': out_of_stock_qs.count(),
        'expired_list': expired_qs,
        'expired_count': expired_qs.count(),
    }

    # Email logic — only send if any alert exists
    if request.method == 'POST' and request.POST.get('action') == 'send_email':
        to_email = getattr(settings, 'ADMIN_EMAIL', None)
        if not to_email:
            messages.error(request, 'Admin email not configured. Set ADMIN_EMAIL in settings.py.')
            return redirect('admin_notifications')

        # Include only conditions that are > 0
        sections = []
        if context['expired_count'] > 0:
            sections.append('Expired Medicines')
        if context['out_of_stock_count'] > 0:
            sections.append('Out of Stock')
        if context['low_stock_count'] > 0:
            sections.append('Low Stock')
        if context['expiring_in_3_days_count'] > 0:
            sections.append('Expiring Soon')

        # If nothing to report
        if not sections:
            messages.info(request, 'No active alerts to email.')
            return redirect('admin_notifications')

        subject = f"Pharmacy Inventory Alert - {', '.join(sections)} ({datetime.now().strftime('%Y-%m-%d %H:%M')})"

        html_content = render_to_string('emails/notifications_summary.html', context)

        # Build text version dynamically
        text_parts = ["Dear Admin,", "", "Here is your pharmacy inventory alert summary:"]
        if context['expired_count'] > 0:
            text_parts.append(f"❌ Expired Medicines: {context['expired_count']}")
        if context['out_of_stock_count'] > 0:
            text_parts.append(f"🚫 Out of Stock: {context['out_of_stock_count']}")
        if context['low_stock_count'] > 0:
            text_parts.append(f"⚠️ Low Stock: {context['low_stock_count']}")
        if context['expiring_in_3_days_count'] > 0:
            text_parts.append(f"🧾 Expiring in 3 Days: {context['expiring_in_3_days_count']}")

        text_parts.append("")
        text_parts.append("Please review these items in the admin dashboard.")
        text_parts.append("Best regards,")
        text_parts.append("💊 Pharmacy Management System")

        text_content = "\n".join(text_parts)

        # Send email
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [to_email]
        )
        email.attach_alternative(html_content, 'text/html')

        try:
            email.send(fail_silently=False)
            messages.success(request, f"Email sent successfully to {to_email}.")
        except Exception as e:
            messages.error(request, f"Failed to send email: {e}")

        return redirect('admin_notifications')

    return render(request, 'notifications.html', context)

# For staff dashboard
@staff_required
def staff_dashboard(request):
    total_medicines = Medicine.objects.count()
    out_of_stock = Medicine.objects.filter(stock_qty__lte=0).count()
    expired_medicines = Medicine.objects.filter(exp_date__lt=timezone.now().date()).count()

    context = {
        'total_medicines': total_medicines,
        'out_of_stock': out_of_stock,
        'expired_medicines': expired_medicines,
    }
    return render(request, 'pharmacist/dashboard.html', context)  # Use same template as pharmacist