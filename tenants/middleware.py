"""
Custom middleware to check if tenant is active before allowing access.
This middleware runs after TenantMainMiddleware to verify tenant status.
"""
from django.http import HttpResponseForbidden
from django_tenants.utils import get_tenant_model, get_public_schema_name, schema_context
from django.db import connection


class TenantActiveMiddleware:
    """
    Middleware to block access to deactivated tenants.
    Must be placed after TenantMainMiddleware in MIDDLEWARE setting.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip check for public schema
        current_schema = connection.schema_name
        public_schema = get_public_schema_name()
        
        if current_schema == public_schema:
            return self.get_response(request)

        # Check if current tenant is active (query from public schema)
        try:
            Tenant = get_tenant_model()
            with schema_context(public_schema):
                tenant = Tenant.objects.get(schema_name=current_schema)
                
                if not tenant.is_active:
                    # Tenant is deactivated, block access
                    return HttpResponseForbidden(
                        '<html><body><h1>Tenant Deactivated</h1>'
                        '<p>This tenant account has been deactivated. Please contact support for assistance.</p>'
                        '</body></html>',
                        content_type='text/html'
                    )
        except Tenant.DoesNotExist:
            # Tenant not found, allow django-tenants to handle it
            pass
        except Exception:
            # If there's any error, allow the request to proceed
            # (better to allow access than block due to a bug)
            pass

        return self.get_response(request)

