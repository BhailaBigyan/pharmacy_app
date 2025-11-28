# Multi-Tenant Migration Guide

This guide explains how to migrate your single-tenant Django pharmacy app to a multi-tenant application using django-tenants.

## Overview

Your application has been converted to use **django-tenants**, which implements multi-tenancy using PostgreSQL schemas. Each tenant (pharmacy) will have its own isolated database schema, ensuring complete data separation.

## Key Changes Made

1. **Installed django-tenants** - Added to `requirements.txt`
2. **Created tenants app** - Contains `Client` and `Domain` models
3. **Updated settings.py** - Configured for multi-tenancy with:
   - `SHARED_APPS` and `TENANT_APPS` separation
   - Tenant middleware
   - PostgreSQL backend for django-tenants
   - Public schema URL configuration
4. **Updated middleware** - Added `TenantMainMiddleware` as the first middleware
5. **Created public URLs** - `urls_public.py` for public schema access
6. **Updated WSGI** - Modified `passenger_wsgi.py` for tenant support

## Database Requirements

**Important**: django-tenants requires PostgreSQL. SQLite is not supported.

Your database configuration in `settings.py` has been updated to use:
```python
'ENGINE': 'django_tenants.postgresql_backend'
```

## Migration Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Initial Migrations

First, create migrations for the tenants app:

```bash
python manage.py makemigrations tenants
```

### 3. Run Migrations for Public Schema

Run migrations on the public schema (this creates the shared tables):

```bash
python manage.py migrate_schemas --shared
```

### 4. Create Your First Tenant

You have two options:

#### Option A: Using Management Command

```bash
python manage.py create_tenant --name "My Pharmacy" --schema my_pharmacy --domain localhost --is-primary
```

#### Option B: Using Web Interface

1. Access the public schema (no tenant subdomain)
2. Navigate to `/tenants/create-tenant/`
3. Fill in the form to create a new tenant

### 5. Run Migrations for Tenant Schemas

After creating a tenant, you need to run migrations for each tenant schema:

```bash
# For a specific tenant
python manage.py migrate_schemas --schema my_pharmacy

# Or for all tenants
python manage.py migrate_schemas
```

### 6. Create Initial Data for Tenant

After migrations, you may want to create initial users and data for each tenant. You can use your existing seed command:

```bash
python manage.py seed_data
```

**Note**: Make sure you're in the tenant schema context when running this.

## How Multi-Tenancy Works

### Schema-Based Isolation

- **Public Schema**: Contains shared tables (tenants, domains, django admin, etc.)
- **Tenant Schemas**: Each tenant has its own schema with all tenant-specific data

### Domain Routing

django-tenants routes requests based on the domain/subdomain:

- `localhost` or `yourdomain.com` → Public schema
- `tenant1.localhost` or `tenant1.yourdomain.com` → Tenant 1 schema
- `tenant2.localhost` or `tenant2.yourdomain.com` → Tenant 2 schema

### Development Setup

For local development, you can:

1. **Use subdomains**: Add entries to `/etc/hosts` (Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` (Windows):
   ```
   127.0.0.1 tenant1.localhost
   127.0.0.1 tenant2.localhost
   ```

2. **Use different ports**: Configure your development server to use different ports for each tenant

3. **Use domain parameter**: Some setups allow passing tenant via URL parameter (requires custom middleware)

## Important Notes

### Model Placement

- Models in `SHARED_APPS` → Stored in public schema (shared across all tenants)
- Models in `TENANT_APPS` → Stored in tenant schemas (isolated per tenant)

All your existing models (User, Medicine, Supplier, Billing, etc.) are in `TENANT_APPS`, so they are tenant-specific.

### User Model

Your custom `User` model is tenant-specific. Each tenant will have its own users. If you need shared users, you would need to move the User model to `SHARED_APPS`, but this is typically not recommended for multi-tenant apps.

### Company Model

The `Company` model is tenant-specific, meaning each tenant can have their own company information.

## Management Commands

django-tenants provides several useful commands:

```bash
# List all tenants
python manage.py list_tenants

# Run migrations for all tenants
python manage.py migrate_schemas

# Run migrations for public schema only
python manage.py migrate_schemas --shared

# Run migrations for specific tenant
python manage.py migrate_schemas --schema tenant_schema_name

# Create a new tenant (custom command)
python manage.py create_tenant --name "Name" --schema schema_name --domain domain.com
```

## Production Deployment

### Domain Configuration

1. Set up DNS to point subdomains to your server
2. Configure your web server (nginx/apache) to handle subdomain routing
3. Ensure SSL certificates cover all tenant subdomains (wildcard SSL recommended)

### Database

- Ensure PostgreSQL is properly configured
- Consider connection pooling for multiple tenants
- Set up proper backups for all schemas

### Static Files

Static files are shared across tenants. If you need tenant-specific static files, you'll need additional configuration.

## Troubleshooting

### "No tenant found" error

- Ensure the domain is properly configured in the `Domain` model
- Check that the domain matches your request (including subdomain)
- Verify `SHOW_PUBLIC_IF_NO_TENANT_FOUND = True` in settings if you want public access

### Migration errors

- Make sure you run `migrate_schemas --shared` first
- Then run `migrate_schemas` for tenant schemas
- Check that all apps are correctly listed in `SHARED_APPS` or `TENANT_APPS`

### Schema not found

- Verify the tenant was created successfully
- Check the schema name matches (case-sensitive)
- Ensure migrations were run for that tenant

## Next Steps

1. **Test the setup**: Create a test tenant and verify data isolation
2. **Migrate existing data**: If you have existing data, you'll need to migrate it to a tenant schema
3. **Update documentation**: Update any user-facing documentation about domain/subdomain access
4. **Configure domains**: Set up proper domain configuration for production

## Additional Resources

- [django-tenants documentation](https://django-tenants.readthedocs.io/)
- [PostgreSQL schemas documentation](https://www.postgresql.org/docs/current/ddl-schemas.html)

