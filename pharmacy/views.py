# ============================
# IMPORTS
# ============================

from datetime import date, timedelta, datetime
import random
import string
import json

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string, render_to_string
from django.utils.html import strip_tags

from medicine.models import Medicine
from medicine.filters import MedicineFilter

from .decorators import (
    admin_required, pharmacist_required,
    staff_required, pharmacist_or_staff_required
)
from .forms import UserRegistrationForm

# ============================
# USER AUTH VIEWS
# ============================

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # Redirect based on role
            if user.role == 'admin':
                return redirect('index')
            elif user.role == 'pharmacist':
                return redirect('pharmacist_dashboard')
            else:
                return redirect('staff_dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect('login')


User = get_user_model()


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            # Generate reset token
            reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            user.reset_token = reset_token
            user.save()

            reset_url = request.build_absolute_uri(f'/reset-password/{reset_token}/')

            subject = 'Password Reset Request'
            message = (
                f'Hi {user.username},\n\n'
                f'You requested a password reset. Click the link below:\n{reset_url}\n\n'
                f'If not requested, please ignore this email.'
            )

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)

            messages.success(request, 'Password reset link sent to your email.')
            return redirect('forgot_password')

        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')

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

                messages.success(request, 'Password reset successful. Please login.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')

    except User.DoesNotExist:
        messages.error(request, 'Invalid reset token.')
        return redirect('login')

    return render(request, 'reset_password.html', {'token': token})


# ============================
# DASHBOARDS & ADMIN PAGES
# ============================

@admin_required
def index(request):
    today = timezone.now().date()
    three_days_from_now = today + timedelta(days=3)

    total_medicines = Medicine.objects.count()
    low_stock_qs = Medicine.objects.filter(stock_qty__gt=0, stock_qty__lte=10)

    out_of_stock = Medicine.objects.filter(stock_qty__lte=0).count()
    expired_medicines = Medicine.objects.filter(exp_date__lt=today).count()

    expiring_in_3_days = Medicine.objects.filter(
        exp_date__gt=today,
        exp_date__lte=three_days_from_now
    ).order_by('exp_date')

    total_notifications = (
        expiring_in_3_days.count() +
        low_stock_qs.count() +
        out_of_stock +
        expired_medicines
    )

    context = {
        'total_medicines': total_medicines,
        'out_of_stock': out_of_stock,
        'expired_medicines': expired_medicines,
        'expiring_in_3_days_count': expiring_in_3_days.count(),
        'expiring_in_3_days_list': expiring_in_3_days[:5],
        'low_stock_count': low_stock_qs.count(),
        'low_stock_list': low_stock_qs[:5],
        'total_notifications': total_notifications,
    }

    if request.user.role == 'admin':
        return render(request, 'admin/dashboard.html', context)
    elif request.user.role == 'pharmacist':
        return redirect('pharmacist_dashboard')
    else:
        return redirect('staff_dashboard')


def stock_report(request):
    today = date.today()
    expiring_soon_date = today + timedelta(days=30)
    medicines = Medicine.objects.all()

    context = {
        "medicines": medicines,
        "today": today,
        "expiring_soon_date": expiring_soon_date,
        "total_medicines": medicines.count(),
        "in_stock": medicines.filter(stock_qty__gt=10).count(),
        "low_stock": medicines.filter(stock_qty__lte=10, stock_qty__gt=0).count(),
        "out_of_stock": medicines.filter(stock_qty__lte=0).count(),
    }

    return render(request, 'admin/stock/stock_report.html', context)


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


# ============================
# PHARMACIST & STAFF DASHBOARDS
# ============================

@pharmacist_or_staff_required
def pharmacist_dashboard(request):
    from billing.models import Invoice, InvoiceItem
    from django.db.models import Sum, Count

    today = timezone.now().date()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)

    total_medicines = Medicine.objects.count()
    out_of_stock = Medicine.objects.filter(stock_qty__lte=0).count()
    expired_medicines = Medicine.objects.filter(exp_date__lt=today).count()

    today_sales = Invoice.objects.filter(created_at__date=today).aggregate(
        total=Sum('total'), count=Count('invoice_id')
    )

    month_sales = Invoice.objects.filter(created_at__date__gte=this_month).aggregate(
        total=Sum('total'), count=Count('invoice_id')
    )

    last_month_sales = Invoice.objects.filter(
        created_at__date__gte=last_month,
        created_at__date__lt=this_month
    ).aggregate(total=Sum('total'), count=Count('invoice_id'))

    top_medicines = InvoiceItem.objects.values('medicine__name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('total')
    ).order_by('-total_sold')[:5]

    recent_transactions = Invoice.objects.all().order_by('-created_at')[:5]

    sales_trend = []
    for i in range(7):
        date_val = today - timedelta(days=i)
        daily_sales = Invoice.objects.filter(created_at__date=date_val).aggregate(
            total=Sum('total')
        )['total'] or 0

        sales_trend.append({
            'date': date_val.strftime('%m/%d'),
            'amount': float(daily_sales)
        })

    sales_trend.reverse()

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
        'sales_trend': json.dumps(sales_trend),
    }

    return render(request, 'pharmacist/dashboard.html', context)


@staff_required
def staff_dashboard(request):
    context = {
        'total_medicines': Medicine.objects.count(),
        'out_of_stock': Medicine.objects.filter(stock_qty__lte=0).count(),
        'expired_medicines': Medicine.objects.filter(exp_date__lt=timezone.now().date()).count(),
    }
    return render(request, 'pharmacist/dashboard.html', context)


# ============================
# NOTIFICATIONS
# ============================

def notifications(request):
    today = timezone.now().date()
    three_months_from_now = today + timedelta(days=90)

    expiring_in_3_months = Medicine.objects.filter(
        exp_date__gt=today, exp_date__lte=three_months_from_now
    )

    low_stock_qs = Medicine.objects.filter(stock_qty__gt=0, stock_qty__lte=10)
    out_of_stock_qs = Medicine.objects.filter(stock_qty__lte=0)
    expired_qs = Medicine.objects.filter(exp_date__lt=today)

    context = {
        'today': today,
        'expiring_in_3_months': expiring_in_3_months,
        'expiring_in_3_months_count': expiring_in_3_months.count(),
        'low_stock_list': low_stock_qs,
        'low_stock_count': low_stock_qs.count(),
        'out_of_stock_list': out_of_stock_qs,
        'out_of_stock_count': out_of_stock_qs.count(),
        'expired_list': expired_qs,
        'expired_count': expired_qs.count(),
    }

    
    # Send email if requested
    if request.method == 'POST' and request.POST.get('action') == 'send_email':
        
        company = Company.objects.first()
        to_email = company.email if company else None

        if not to_email:
            messages.error(request, 'Admin email not configured.')
            return redirect('notifications')

        sections = []
        if context['expired_count'] > 0: sections.append('Expired Medicines')
        if context['out_of_stock_count'] > 0: sections.append('Out of Stock')
        if context['low_stock_count'] > 0: sections.append('Low Stock')
        if context['expiring_in_3_months_count'] > 0: sections.append('Expiring Soon')

        if not sections:
            messages.info(request, 'No active alerts to email.')
            return redirect('notifications')

        subject = f"Pharmacy Inventory Alert - {', '.join(sections)} ({datetime.now().strftime('%Y-%m-%d %H:%M')})"

        html_content = render_to_string('emails/notifications_summary.html', context)

        text_parts = [
            "Dear Admin,", "", "Here is your pharmacy inventory alert summary:"
        ]

        if context['expired_count'] > 0:
            text_parts.append(f"❌ Expired Medicines: {context['expired_count']}")
        if context['out_of_stock_count'] > 0:
            text_parts.append(f"🚫 Out of Stock: {context['out_of_stock_count']}")
        if context['low_stock_count'] > 0:
            text_parts.append(f"⚠️ Low Stock: {context['low_stock_count']}")
        if context['expiring_in_3_months_count'] > 0:
            text_parts.append(f"🧾 Expiring in 3 Months: {context['expiring_in_3_months_count']}")

        text_parts += ["", "Please review the items in the admin dashboard.", "Best regards,", "Pharmacy Management System"]

        text_content = "\n".join(text_parts)

        email = EmailMultiAlternatives(
            subject, text_content, settings.DEFAULT_FROM_EMAIL, [to_email]
        )
        email.attach_alternative(html_content, 'text/html')

        try:
            email.send()
            messages.success(request, f"Email sent successfully to {to_email}.")
        except Exception as e:
            messages.error(request, f"Failed to send email: {e}")

        return redirect('notifications')

    return render(request, 'notifications.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Company 
# Assuming admin_required is a custom decorator defined elsewhere, 
# e.g., in decorators.py or a user authentication module
# from .decorators import admin_required 

# Placeholder for admin_required if it's not defined in the environment
# For demonstration purposes, we'll assume it exists or use a simple function.
def admin_required(view_func):
    """Placeholder for admin_required decorator."""
    return view_func

@admin_required
def company_register(request):
    """Handles the company registration form submission."""
    if request.method == "POST":
        company_name = request.POST.get("company_name")
        address = request.POST.get("address")
        phone_number = request.POST.get("phone_number")
        
        # New fields from the updated form
        email = request.POST.get("email")
        pan_number = request.POST.get("pan_number")
        vat_number = request.POST.get("vat_number")

        # Basic validation (You should add more robust validation later)
        if not company_name or not address or not phone_number:
            messages.error(request, "Company Name, Address, and Phone Number are required fields.")
            return render(request, "company_registration.html")

        # Create the Company object
        try:
            Company.objects.create(
                company_name=company_name,
                address=address,
                phone_number=phone_number,
                email=email if email else None,
                pan_number=pan_number if pan_number else None,
                vat_number=vat_number if vat_number else None,
            )
            messages.success(request, f"Company '{company_name}' registered successfully.")
            return redirect('company_register') # Redirects to clear the form
            
        except Exception as e:
            # Catch database or server errors
            messages.error(request, f"An error occurred during registration: {e}")
            
    return render(request, "company_registration.html")