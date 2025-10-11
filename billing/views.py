from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum
from django.utils.dateparse import parse_date
import json

from .models import Invoice, InvoiceItem
from medicine.models import Medicine  # ✅ correct import

# -------------------------------
# Billing Page
# -------------------------------
def bill(request):
    medicines = Medicine.objects.all().order_by('name')
    return render(request, 'pharmacist/billing/billing.html', {'medicines': medicines})

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
            items = data.get("items", [])

            # Create invoice
            invoice = Invoice.objects.create(
                customer_name=customer_name,
                phone_number=phone_number,
                payment_method=payment_method,
                subtotal=subtotal,
                tax=tax,
                total=total,
            )

            # Create invoice items
            for item in items:
                med = Medicine.objects.get(medicine_id=item["id"])
                InvoiceItem.objects.create(
                    invoice=invoice,
                    medicine=med,
                    quantity=item["qty"],
                    price=item["price"],
                    total=item["price"] * item["qty"]
                )
                med.stock -= item["qty"]
                med.save()

            return JsonResponse({"invoice_id": invoice.invoice_id})

        except Exception as e:
            print("Error:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)


# -------------------------------
# Invoice Detail View
# -------------------------------
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    items = invoice.items.all()  # optional, you can also use invoice.items in template directly
    return render(request, "pharmacist/billing/invoice_detail.html", {
        "invoice": invoice,
        "items": items,
    })

# -------------------------------
# Sales Report
# -------------------------------
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
    return render(request, "pharmacist/billing/sales_report.html", context)
