from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import Client, Domain


@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'schema_name', 'tenant_code', 'is_active', 'created_on')
    list_filter = ('is_active', 'created_on')
    search_fields = ('name', 'schema_name', 'tenant_code')
    list_editable = ('is_active',)  # Allow quick toggle in list view
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'schema_name', 'tenant_code', 'is_active')
        }),
        ('Access Control', {
            'fields': ('access_pin',)
        }),
        ('Database Configuration', {
            'fields': ('subdomain', 'db_name', 'db_user', 'db_password', 'db_host', 'db_port'),
            'classes': ('collapse',)
        }),
        ('Advanced', {
            'fields': ('auto_create_schema', 'auto_drop_schema', 'created_on'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_on',)


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')

