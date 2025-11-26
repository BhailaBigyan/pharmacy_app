"""
Django management command to seed the database with minimal data.
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from pharmacy.models import Company
from supplier.models import Supplier, SupplierInvoice, SupplierInvoiceItem
from medicine.models import Medicine
from billing.models import Customer, Invoice, InvoiceItem

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with minimal data for testing and development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        # Seed data in order of dependencies
        self.seed_company()
        self.seed_users()
        self.seed_suppliers()
        self.seed_medicines()
        self.seed_customers()
        self.seed_sample_invoice()

        self.stdout.write(self.style.SUCCESS('\n[SUCCESS] Database seeding completed successfully!'))

    def clear_data(self):
        """Clear existing data (optional)"""
        InvoiceItem.objects.all().delete()
        Invoice.objects.all().delete()
        Customer.objects.all().delete()
        Medicine.objects.all().delete()
        SupplierInvoiceItem.objects.all().delete()
        SupplierInvoice.objects.all().delete()
        Supplier.objects.all().delete()
        Company.objects.all().delete()
        # Don't delete users, keep admin user
        User.objects.exclude(username='admin').delete()
        self.stdout.write(self.style.SUCCESS('  [OK] Existing data cleared'))

    def seed_company(self):
        """Seed Company data"""
        self.stdout.write('Seeding Company...')
        
        company, created = Company.objects.get_or_create(
            company_name='Sample Pharmacy',
            defaults={
                'address': '123 Main Street, City, State',
                'phone_number': '+1234567890',
                'email': 'info@samplepharmacy.com',
                'pan_number': 'ABCDE1234F',
                'vat_number': 'VAT123456',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'  [OK] Created company: {company.company_name}'))
        else:
            self.stdout.write(self.style.WARNING(f'  - Company already exists: {company.company_name}'))

    def seed_users(self):
        """Seed User data"""
        self.stdout.write('Seeding Users...')
        
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@pharmacy.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'password': 'admin123',
                'is_superuser': True,
                'is_staff': True,
            },
            {
                'username': 'pharmacist',
                'email': 'pharmacist@pharmacy.com',
                'first_name': 'John',
                'last_name': 'Pharmacist',
                'role': 'pharmacist',
                'password': 'pharmacist123',
            },
            {
                'username': 'staff',
                'email': 'staff@pharmacy.com',
                'first_name': 'Jane',
                'last_name': 'Staff',
                'role': 'staff',
                'password': 'staff123',
            },
        ]
        
        for user_data in users_data:
            password = user_data.pop('password')
            is_superuser = user_data.pop('is_superuser', False)
            is_staff = user_data.pop('is_staff', False)
            
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            
            if created:
                user.set_password(password)
                user.is_superuser = is_superuser
                user.is_staff = is_staff
                user.save()
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created user: {user.username} (role: {user.role})'))
            else:
                self.stdout.write(self.style.WARNING(f'  - User already exists: {user.username}'))

    def seed_suppliers(self):
        """Seed Supplier data"""
        self.stdout.write('Seeding Suppliers...')
        
        suppliers_data = [
            {
                'name': 'ABC Pharmaceuticals',
                'contact': '+1234567890',
                'email': 'contact@abcpharma.com',
                'address': '456 Pharma Street, Industrial Area',
                'pan_number': 'PHARMA1234A',
            },
            {
                'name': 'XYZ Medical Supplies',
                'contact': '+0987654321',
                'email': 'info@xyzmedical.com',
                'address': '789 Medical Road, Business District',
                'pan_number': 'MEDICAL5678B',
            },
        ]
        
        suppliers = []
        for supplier_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=supplier_data['name'],
                defaults=supplier_data
            )
            suppliers.append(supplier)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created supplier: {supplier.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  - Supplier already exists: {supplier.name}'))
        
        return suppliers

    def seed_medicines(self):
        """Seed Medicine data"""
        self.stdout.write('Seeding Medicines...')
        
        # Get or create suppliers first
        suppliers = list(Supplier.objects.all())
        if not suppliers:
            self.stdout.write(self.style.ERROR('  ✗ No suppliers found. Please seed suppliers first.'))
            return
        
        # Calculate dates
        today = date.today()
        mfg_date = today - timedelta(days=180)  # 6 months ago
        exp_date = today + timedelta(days=365)  # 1 year from now
        
        medicines_data = [
            {
                'name': 'Paracetamol',
                'brand_name': 'Tylenol',
                'batch_number': 'BATCH001',
                'category': 'tablet/capsule',
                'mfg_date': mfg_date,
                'exp_date': exp_date,
                'price': 10.50,
                'stock_qty': 100,
                'supplier': suppliers[0],
            },
            {
                'name': 'Ibuprofen',
                'brand_name': 'Advil',
                'batch_number': 'BATCH002',
                'category': 'tablet/capsule',
                'mfg_date': mfg_date,
                'exp_date': exp_date,
                'price': 15.75,
                'stock_qty': 75,
                'supplier': suppliers[0],
            },
            {
                'name': 'Cough Syrup',
                'brand_name': 'Robitussin',
                'batch_number': 'BATCH003',
                'category': 'syrup',
                'mfg_date': mfg_date,
                'exp_date': exp_date,
                'price': 25.00,
                'stock_qty': 50,
                'supplier': suppliers[1],
            },
            {
                'name': 'Antibiotic Ointment',
                'brand_name': 'Neosporin',
                'batch_number': 'BATCH004',
                'category': 'ointment',
                'mfg_date': mfg_date,
                'exp_date': exp_date,
                'price': 12.50,
                'stock_qty': 60,
                'supplier': suppliers[1],
            },
        ]
        
        for medicine_data in medicines_data:
            supplier = medicine_data.pop('supplier')
            medicine, created = Medicine.objects.get_or_create(
                name=medicine_data['name'],
                brand_name=medicine_data['brand_name'],
                batch_number=medicine_data['batch_number'],
                defaults={**medicine_data, 'supplier': supplier}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created medicine: {medicine.name} ({medicine.brand_name})'))
            else:
                self.stdout.write(self.style.WARNING(f'  - Medicine already exists: {medicine.name}'))

    def seed_customers(self):
        """Seed Customer data"""
        self.stdout.write('Seeding Customers...')
        
        customers_data = [
            {
                'name': 'John Doe',
                'email': 'john.doe@email.com',
                'phone_number': '+1111111111',
                'address': '123 Customer Street',
            },
            {
                'name': 'Jane Smith',
                'email': 'jane.smith@email.com',
                'phone_number': '+2222222222',
                'address': '456 Client Avenue',
            },
        ]
        
        for customer_data in customers_data:
            customer, created = Customer.objects.get_or_create(
                phone_number=customer_data['phone_number'],
                defaults=customer_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created customer: {customer.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  - Customer already exists: {customer.name}'))

    def seed_sample_invoice(self):
        """Seed a sample Invoice with items"""
        self.stdout.write('Seeding Sample Invoice...')
        
        # Get a customer
        customer = Customer.objects.first()
        if not customer:
            self.stdout.write(self.style.WARNING('  - No customer found, skipping invoice creation'))
            return
        
        # Get some medicines
        medicines = Medicine.objects.all()[:2]
        if not medicines.exists():
            self.stdout.write(self.style.WARNING('  - No medicines found, skipping invoice creation'))
            return
        
        # Check if sample invoice already exists
        if Invoice.objects.filter(customer_name=customer.name, billed_by='admin').exists():
            self.stdout.write(self.style.WARNING('  - Sample invoice already exists, skipping'))
            return
        
        # Create invoice
        invoice = Invoice.objects.create(
            customer=customer,
            customer_name=customer.name,
            phone_number=customer.phone_number,
            payment_method='cash',
            subtotal=0,
            discount=0,
            total=0,
            billed_by='admin',
        )
        
        # Calculate totals
        subtotal = 0
        for medicine in medicines:
            quantity = 2
            price = float(medicine.price)
            total = price * quantity
            subtotal += total
            
            InvoiceItem.objects.create(
                invoice=invoice,
                medicine=medicine,
                quantity=quantity,
                price=price,
                total=total
            )
        
        invoice.subtotal = subtotal
        invoice.discount = 0
        invoice.total = subtotal
        invoice.save()
        
        self.stdout.write(self.style.SUCCESS(f'  [OK] Created sample invoice: #{invoice.invoice_id}'))

