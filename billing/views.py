from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from pharmacy.decorators import pharmacist_or_staff_required, transaction_atomic

import json

from .models import Invoice, InvoiceItem, Customer
from medicine.models import Medicine


# -------------------------------
# Billing Page
# -------------------------------
@pharmacist_or_staff_required
def bill(request):
    medicines = Medicine.objects.all().order_by('name')
    return render(request, 'pharmacist/billing/billing_new.html', {'medicines': medicines})


# -------------------------------
# Generate Invoice (AJAX POST)
# -------------------------------
@csrf_exempt
@transaction_atomic
def generate_invoice(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)

        # -------------------------------
        # Extract Data
        # -------------------------------
        customer_name = data.get("customerName")
        phone_number = data.get("phoneNumber")
        payment_method = data.get("paymentMethod")
        subtotal = data.get("subtotal")
        discount = data.get("discount")  # currency amount
        total = data.get("total")
        billed_by = request.user.username
        items = data.get("items", [])

        # -------------------------------
        # Validate Required Fields
        # -------------------------------
        if not customer_name:
            return JsonResponse({"error": "Customer name is required"}, status=400)
        if not payment_method:
            return JsonResponse({"error": "Payment method is required"}, status=400)
        if not items:
            return JsonResponse({"error": "At least one item is required"}, status=400)
        if subtotal is None or total is None:
            return JsonResponse({"error": "Subtotal and total are required"}, status=400)

        # -------------------------------
        # Validate Discount
        # -------------------------------
        try:
            discount = float(discount) if discount else 0.0
            if discount < 0:
                return JsonResponse({"error": "Discount cannot be negative"}, status=400)
            if discount > float(subtotal):
                return JsonResponse({"error": "Discount cannot exceed subtotal"}, status=400)
        except ValueError:
            return JsonResponse({"error": "Invalid discount value"}, status=400)

        # -------------------------------
        # Helper: Clean numeric inputs
        # -------------------------------
        def clean_currency(value):
            if not value or str(value).strip() in ["", "Insufficient"]:
                return None
            try:
                return float(str(value).replace("$", "").replace("NRS", "").strip())
            except ValueError:
                return None

        amount_received = clean_currency(data.get("amountReceived"))
        return_amount = clean_currency(data.get("returnAmount"))

        # -------------------------------
        # Get or Create Customer
        # -------------------------------
        customer, _ = Customer.objects.get_or_create(
            phone_number=phone_number if phone_number else None,
            defaults={"name": customer_name}
        )

        # -------------------------------
        # Create Invoice
        # -------------------------------
        invoice = Invoice.objects.create(
            customer=customer,
            customer_name=customer_name,
            phone_number=phone_number,
            payment_method=payment_method,
            amount_received=amount_received,
            return_amount=return_amount,
            subtotal=subtotal,
            discount=discount,  # store discount amount
            total=total,
            billed_by=billed_by,
            created_at=timezone.now(),
        )

        # -------------------------------
        # Create Invoice Items & Update Stock
        # -------------------------------
        for item in items:
            medicine_id = item.get("id")
            quantity = item.get("qty")
            price = item.get("price")

            med = Medicine.objects.filter(medicine_id=medicine_id).first()
            if not med:
                raise ValueError(f"Medicine with ID {medicine_id} not found")

            if med.stock_qty < quantity:
                raise ValueError(
                    f"Insufficient stock for {med.name}. "
                    f"Available: {med.stock_qty}, Requested: {quantity}"
                )

            InvoiceItem.objects.create(
                invoice=invoice,
                medicine=med,
                quantity=quantity,
                price=price,
                total=price * quantity
            )

            # Deduct stock
            med.stock_qty -= quantity
            med.save()

        return JsonResponse({"invoice_id": invoice.invoice_id}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)


# -------------------------------
# Invoice Detail View
# -------------------------------
@pharmacist_or_staff_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    items = invoice.items.all()
    
    return render(request, "pharmacist/billing/invoice_detail_new.html", {
        "invoice": invoice,
        "items": items,
    })


# -------------------------------
# Sales Report
# -------------------------------
@pharmacist_or_staff_required
def sales_report(request):
    invoices = Invoice.objects.all().order_by("-created_at")

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date and end_date:
        invoices = invoices.filter(
            created_at__date__gte=parse_date(start_date),
            created_at__date__lte=parse_date(end_date)
        )

    total_sales = invoices.aggregate(total=Sum("total"))["total"] or 0
    total_discount = invoices.aggregate(discount=Sum("discount"))["discount"] or 0
    total_transactions = invoices.count()

    context = {
        "invoices": invoices,
        "total_sales": total_sales,
        "total_discount": total_discount,
        "total_transactions": total_transactions,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "pharmacist/billing/sales_report_new.html", context)


# -------------------------------
# Customer List & Detail
# -------------------------------
@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('-created_at')
    return render(request, 'pharmacist/billing/customer_list.html', {
        'customers': customers,
    })


@login_required
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, customer_id=customer_id)
    invoices = customer.invoices.all().order_by('-created_at')
    items = InvoiceItem.objects.filter(invoice__in=invoices).select_related('medicine', 'invoice')

    total_spent = sum(inv.total for inv in invoices)
    total_orders = invoices.count()
    total_items = sum(item.quantity for item in items)

    return render(request, 'pharmacist/billing/customer_detail.html', {
        'customer': customer,
        'invoices': invoices,
        'items': items,
        'total_spent': total_spent,
        'total_orders': total_orders,
        'total_items': total_items,
    })
