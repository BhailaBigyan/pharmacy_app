from django.core.management.base import BaseCommand
from tenants.models import Client, Domain


class Command(BaseCommand):
    help = 'Create a new tenant (custom command - use create_tenant_custom to avoid conflict)'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, help='Tenant name', required=True)
        parser.add_argument('--schema', type=str, help='Schema name (must be lowercase, no spaces)', required=True)
        parser.add_argument('--domain', type=str, help='Domain name (e.g., example.com or localhost)', required=True)
        parser.add_argument('--is-primary', action='store_true', help='Set as primary domain', default=True)

    def handle(self, *args, **options):
        name = options['name']
        schema_name = options['schema']
        domain_name = options['domain']
        is_primary = options.get('is_primary', True)

        # Validate schema name (must be lowercase, alphanumeric + underscore)
        if not schema_name.replace('_', '').islower() or not schema_name.replace('_', '').isalnum():
            self.stdout.write(
                self.style.ERROR('Schema name must be lowercase and contain only letters, numbers, and underscores')
            )
            return

        try:
            # Create tenant
            tenant = Client.objects.create(
                name=name,
                schema_name=schema_name,
            )

            # Create domain
            domain = Domain.objects.create(
                domain=domain_name,
                tenant=tenant,
                is_primary=is_primary,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created tenant "{name}" with schema "{schema_name}" and domain "{domain_name}"'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    f'Note: You need to run migrations for this tenant: '
                    f'python manage.py migrate_schemas --schema {schema_name}'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating tenant: {str(e)}')
            )

