# Quick Start Guide - Multi-Tenant Setup

## Prerequisites

- PostgreSQL database (required for django-tenants)
- Python 3.x
- All dependencies installed

## Initial Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Migrations
```bash
python manage.py makemigrations tenants
```

### 3. Run Public Schema Migrations
```bash
python manage.py migrate_schemas --shared
```

### 4. Create Your First Tenant

**Option A: Command Line**
```bash
python manage.py create_tenant --name "My Pharmacy" --schema my_pharmacy --domain localhost --is-primary
```

**Option B: Web Interface**
- Access your site at the base domain (no subdomain)
- Navigate to `/tenants/create-tenant/`
- Fill in the form

### 5. Run Tenant Migrations
```bash
# For specific tenant
python manage.py migrate_schemas --schema my_pharmacy

# Or for all tenants
python manage.py migrate_schemas
```

## Accessing Tenants

### Development (Local)

1. **Add to hosts file** (Windows: `C:\Windows\System32\drivers\etc\hosts`, Linux/Mac: `/etc/hosts`):
   ```
   127.0.0.1 tenant1.localhost
   127.0.0.1 tenant2.localhost
   ```

2. **Access tenants**:
   - Public schema: `http://localhost:8000`
   - Tenant 1: `http://tenant1.localhost:8000`
   - Tenant 2: `http://tenant2.localhost:8000`

### Production

- Configure DNS to point subdomains to your server
- Each tenant gets its own subdomain: `tenant1.yourdomain.com`, `tenant2.yourdomain.com`

## Important Commands

```bash
# List all tenants
python manage.py list_tenants

# Create tenant
python manage.py create_tenant --name "Name" --schema schema_name --domain domain.com

# Run migrations for all tenants
python manage.py migrate_schemas

# Run migrations for public schema only
python manage.py migrate_schemas --shared

# Run migrations for specific tenant
python manage.py migrate_schemas --schema tenant_schema_name
```

## Default Admin User

Each tenant automatically gets a default admin user:
- Username: `admin`
- Password: `admin123`
- Email: `bigyanbhaila98@gmail.com`

**Important**: Change this password in production!

## Data Isolation

- Each tenant has completely isolated data
- Users, medicines, suppliers, invoices are all tenant-specific
- No data can leak between tenants

## Troubleshooting

- **"No tenant found"**: Check domain configuration in admin or database
- **Migration errors**: Ensure you ran `migrate_schemas --shared` first
- **Schema errors**: Verify tenant was created and migrations were run

For detailed information, see `MULTI_TENANT_MIGRATION_GUIDE.md`

