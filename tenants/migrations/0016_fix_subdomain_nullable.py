# Generated manually to fix subdomain nullable constraint

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0015_fix_db_port_nullable'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE tenants_client ALTER COLUMN subdomain DROP NOT NULL;",
            reverse_sql="ALTER TABLE tenants_client ALTER COLUMN subdomain SET NOT NULL;",
        ),
    ]
