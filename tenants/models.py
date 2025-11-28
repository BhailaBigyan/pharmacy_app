from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django_tenants.models import TenantMixin, DomainMixin


class Client(TenantMixin):
    name = models.CharField(max_length=100)
    tenant_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    access_pin = models.CharField(max_length=128, blank=True, null=True)
    created_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True, help_text="Uncheck to deactivate this tenant and prevent access")
    auto_create_schema = True

    # default true, schema will be automatically created and synced when it is saved
    auto_drop_schema = False  # default false, schema will not be automatically deleted
    
    # Make TenantMixin fields optional since we're using schema-based multi-tenancy
    # These fields are for database-per-tenant approach, not needed for schema-per-tenant
    subdomain = models.CharField(max_length=100, blank=True, null=True)
    db_name = models.CharField(max_length=100, blank=True, null=True)
    db_user = models.CharField(max_length=100, blank=True, null=True)
    db_password = models.CharField(max_length=100, blank=True, null=True)
    db_host = models.CharField(max_length=100, blank=True, null=True)
    db_port = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.name

    def set_access_pin(self, raw_pin: str):
        if not raw_pin:
            self.access_pin = None
        else:
            self.access_pin = make_password(raw_pin)

    def check_access_pin(self, raw_pin: str) -> bool:
        if not self.access_pin:
            return False
        return check_password(raw_pin, self.access_pin)


class Domain(DomainMixin):
    pass

