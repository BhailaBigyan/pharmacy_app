from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django_tenants.utils import schema_context, get_public_schema_name

from .models import Client, Domain


def create_tenant_view(request):
    """
    Public view for creating a new tenant.
    This should only be accessible from the public schema.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        domain_name = request.POST.get('domain')
        schema_name = request.POST.get('schema', slugify(name))
        tenant_code = request.POST.get('tenant_code') or schema_name
        access_pin = request.POST.get('access_pin')

        if not name or not domain_name or not tenant_code or not access_pin:
            messages.error(request, 'Name, domain, tenant code, and access PIN are required fields.')
            return render(request, 'tenants/create_tenant.html')

        # Validate schema name
        if not schema_name.replace('_', '').islower() or not schema_name.replace('_', '').isalnum():
            messages.error(request, 'Schema name must be lowercase and contain only letters, numbers, and underscores.')
            return render(request, 'tenants/create_tenant.html')

        # Validate tenant code
        normalized_code = tenant_code.replace('-', '_').lower()
        if not normalized_code.replace('_', '').isalnum():
            messages.error(request, 'Tenant code must contain only letters, numbers, underscores, or dashes.')
            return render(request, 'tenants/create_tenant.html')

        try:
            public_schema = get_public_schema_name()

            # Check if schema name already exists
            with schema_context(public_schema):
                if Client.objects.filter(schema_name=schema_name).exists():
                    messages.error(request, f'Schema name "{schema_name}" already exists. Please choose another.')
                    return render(request, 'tenants/create_tenant.html')

                # Check if domain already exists
                if Domain.objects.filter(domain=domain_name).exists():
                    messages.error(request, f'Domain "{domain_name}" already exists. Please choose another.')
                    return render(request, 'tenants/create_tenant.html')

                # Check if tenant code already exists
                if Client.objects.filter(tenant_code__iexact=tenant_code).exists():
                    messages.error(request, f'Tenant code "{tenant_code}" already exists. Please choose another.')
                    return render(request, 'tenants/create_tenant.html')

                # Create tenant
                tenant = Client.objects.create(
                    name=name,
                    schema_name=schema_name,
                    tenant_code=tenant_code,
                )
                tenant.set_access_pin(access_pin)
                tenant.save(update_fields=['access_pin'])

                # Create domain
                Domain.objects.create(
                    domain=domain_name,
                    tenant=tenant,
                    is_primary=True,
                )

            messages.success(
                request,
                f'Tenant "{name}" created successfully! '
                f'You can now access it at http://{domain_name}.localhost:8000/ '
                f'Note: You need to run migrations for this tenant.'
            )
            return redirect('create_tenant')

        except Exception as e:
            messages.error(request, f'Error creating tenant: {str(e)}')

    return render(request, 'tenants/create_tenant.html')


def tenant_access_view(request):
    """
    Public view used to verify tenant identity before redirecting to their login page.
    """
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        pin = request.POST.get('access_pin', '').strip()

        if not identifier or not pin:
            messages.error(request, 'Tenant code or domain and PIN are required.')
            return render(request, 'tenants/tenant_access.html')

        client = Client.objects.filter(tenant_code__iexact=identifier).first()

        if not client:
            domain = Domain.objects.filter(domain__iexact=identifier).select_related('tenant').first()
            if domain:
                client = domain.tenant

        if not client:
            messages.error(request, 'Tenant not found. Please check the code or domain.')
            return render(request, 'tenants/tenant_access.html')

        # Check if tenant is active
        if not client.is_active:
            messages.error(request, 'This tenant account has been deactivated. Please contact support.')
            return render(request, 'tenants/tenant_access.html')

        if not client.check_access_pin(pin):
            messages.error(request, 'Invalid PIN for the specified tenant.')
            return render(request, 'tenants/tenant_access.html')

        primary_domain = client.domains.filter(is_primary=True).first()
        if not primary_domain:
            messages.error(request, 'No domain is configured for this tenant. Please contact support.')
            return render(request, 'tenants/tenant_access.html')

        secure = getattr(settings, 'SECURE_SSL_REDIRECT', False) or request.is_secure()
        scheme = 'https' if secure else 'http'
        login_url = f"{scheme}://{primary_domain.domain}.localhost:8000/login/"
        return redirect(login_url)

    return render(request, 'tenants/tenant_access.html')

