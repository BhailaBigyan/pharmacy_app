# Pharmacy Management System

A web-based application to streamline and automate pharmacy operations. It helps pharmacists and administrators efficiently manage medicines, suppliers, customers, stock, sales, billing, and reporting.

---

## Features
- [@bhailabigyan](https://www.github.com/bhailabigyan)
- [@sinkhwalsubash](https://www.github.com/sinkhwal07)

- **Medicine Management:** Add, edit, delete, and view medicines. Track expiry and stock status.
- **Supplier Management:** Manage supplier information.
- **Customer History:** View customers purchase history.
- **Stock Reports:** View low stock, out-of-stock, and expired medicines.
- **Billing & Sales:** Create invoices, manage sales, and view sales reports.
- **User Management:** Admins can manage users and assign roles (Admin, Pharmacist, Staff).
- **Notifications:** Alerts for low stock, out-of-stock, and expiring medicines.
- **Role-Based Access:** Different dashboards and permissions for Admin, Pharmacist, and Staff.

---

## Project Structure

```
pharmacy_app/
│
├── billing/                # Billing and sales logic
├── medicine/               # Medicine management
├── pharmacist/             # Pharmacist-specific views
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── manage.py               # Django management script
└── README.md               # Project documentation
```

---

## Installation & Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
3. **Start the server**
   ```bash
   python manage.py runserver
   ```

---

## Default Admin
   admin_username = "admin"
   admin_password = "Admin@123"

---
## User Roles

- **Admin:** Full access, including user management.
- **Pharmacist:** Billing, medicine management, stock reports.
- **Staff:** Limited access (billing, medicine management).

---

## Key URLs

- `/admin/` — Admin dashboard
- `/pharmacist/` — Pharmacist dashboard
- `/medicine/list_medicine/` — List all medicines
- `/medicine/expired/` — Expired medicines
- `/medicine/stock_out/` — Out-of-stock medicines
- `/billing/bill/` — New bill/invoice
- `/billing/sales_report/` — Sales report

---

## Running Tests

```bash
python manage.py test
```

---

## For any Database Related Error

-For restarting new database
```bash
del pharmacy\migrations\0*.py
del billing\migrations\0*.py
del supplier\migrations\0*.py
del medicine\migrations\0*.py
python manage.py makemigrations
python manage.py migrate
```
## Authors

- [@bhailabigyan](https://www.github.com/bhailabigyan)
- [@sinkhwalsubash](https://www.github.com/sinkhwal07)

---

## License

All right reserved to Bigyan Bhaila.
