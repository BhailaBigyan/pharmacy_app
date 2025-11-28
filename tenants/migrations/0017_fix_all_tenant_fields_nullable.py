# Generated manually to fix all TenantMixin fields to be nullable

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0016_fix_subdomain_nullable'),
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE tenants_client ALTER COLUMN db_name DROP NOT NULL;
            ALTER TABLE tenants_client ALTER COLUMN db_user DROP NOT NULL;
            ALTER TABLE tenants_client ALTER COLUMN db_password DROP NOT NULL;
            ALTER TABLE tenants_client ALTER COLUMN db_host DROP NOT NULL;
            """,
            reverse_sql="""
            ALTER TABLE tenants_client ALTER COLUMN db_name SET NOT NULL;
            ALTER TABLE tenants_client ALTER COLUMN db_user SET NOT NULL;
            ALTER TABLE tenants_client ALTER COLUMN db_password SET NOT NULL;
            ALTER TABLE tenants_client ALTER COLUMN db_host SET NOT NULL;
            """,
        ),
    ]
