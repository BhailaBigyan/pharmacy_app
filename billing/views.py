from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from pharmacy import admin
from pharmacy.decorators import pharmacist_or_staff_required
import json

from .models import Invoice, InvoiceItem, Customer
from medicine.models import Medicine  # ✅ correct import

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
def generate_invoice(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            customer_name = data.get("customerName")
            phone_number = data.get("phoneNumber")
            payment_method = data.get("paymentMethod")
            subtotal = data.get("subtotal")
            tax = data.get("tax")
            total = data.get("total")
            billed_by = request.user.username
            items = data.get("items", [])

            # Validate required fields
            if not customer_name:
                return JsonResponse({"error": "Customer name is required"}, status=400)
            if not payment_method:
                return JsonResponse({"error": "Payment method is required"}, status=400)
            if not items or len(items) == 0:
                return JsonResponse({"error": "At least one item is required"}, status=400)
            if subtotal is None or tax is None or total is None:
                return JsonResponse({"error": "Subtotal, tax, and total are required"}, status=400)

            # Handle amount received and return amount (convert empty strings to None)
            amount_received = data.get("amountReceived")
            return_amount = data.get("returnAmount")
            
            # Convert empty strings to None for decimal fields
            if amount_received == "" or amount_received is None:
                amount_received = None
            else:
                # Remove currency symbols if present
                amount_received_str = str(amount_received).replace("$", "").replace("NRS ", "")
                if amount_received_str == "":
                    amount_received = None
                else:
                    try:
                        amount_received = float(amount_received_str)
                    except ValueError:
                        return JsonResponse({"error": "Invalid amount received value"}, status=400)
                
            if return_amount == "" or return_amount is None:
                return_amount = None
            else:
                # Remove currency symbols if present
                return_amount_str = str(return_amount).replace("$", "").replace("NRS ", "")
                if return_amount_str == "" or return_amount_str == "Insufficient":
                    return_amount = None
                else:
                    try:
                        return_amount = float(return_amount_str)
                    except ValueError:
                        return JsonResponse({"error": "Invalid return amount value"}, status=400)

            # Find or create customer (by phone when provided else by name)
            customer = None
            if phone_number:
                customer, _ = Customer.objects.get_or_create(
                    phone_number=phone_number,
                    defaults={"name": customer_name}
                )
            else:
                customer, _ = Customer.objects.get_or_create(
                    name=customer_name,
                )

            # Create invoice
            invoice = Invoice.objects.create(
                customer=customer,
                customer_name=customer_name,
                phone_number=phone_number,
                payment_method=payment_method,
                amount_received=amount_received,
                return_amount=return_amount,
                subtotal=subtotal,
                tax=tax,
                total=total,
                billed_by=billed_by,
                created_at=timezone.now(),
            )

            # Create invoice items
            for item in items:
                try:
                    med = Medicine.objects.get(medicine_id=item["id"])
                except Medicine.DoesNotExist:
                    return JsonResponse({"error": f"Medicine with ID {item['id']} not found"}, status=400)
                
                # Check if enough stock is available
                if med.stock_qty < item["qty"]:
                    invoice.delete()  # Delete the invoice if insufficient stock
                    return JsonResponse({"error": f"Insufficient stock for {med.name}. Available: {med.stock_qty}, Requested: {item['qty']}"}, status=400)
                
                InvoiceItem.objects.create(
                    invoice=invoice,
                    medicine=med,
                    quantity=item["qty"],
                    price=item["price"],
                    total=item["price"] * item["qty"]
                )
                med.stock_qty -= item["qty"]
                med.save()

            return JsonResponse({"invoice_id": invoice.invoice_id})

        except json.JSONDecodeError as e:
            print("JSON Error:", e)
            return JsonResponse({"error": f"Invalid JSON data: {str(e)}"}, status=400)
        except KeyError as e:
            print("Missing field:", e)
            return JsonResponse({"error": f"Missing required field: {str(e)}"}, status=400)
        except ValueError as e:
            print("Value Error:", e)
            return JsonResponse({"error": f"Invalid value: {str(e)}"}, status=400)
        except Exception as e:
            print("Unexpected Error:", e)
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)


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
    invoices = Invoice.objects.all().order_by("-created_at")  # ✅ fixed

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date and end_date:
        invoices = invoices.filter(
            created_at__date__gte=parse_date(start_date),
            created_at__date__lte=parse_date(end_date)
        )

    total_sales = invoices.aggregate(total=Sum("total"))["total"] or 0
    total_tax = invoices.aggregate(tax=Sum("tax"))["tax"] or 0
    total_transactions = invoices.count()

    context = {
        "invoices": invoices,
        "total_sales": total_sales,
        "total_tax": total_tax,
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
    # Flatten purchased items across invoices
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
