# Generated manually to fix db_port nullable constraint

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0014_make_db_port_nullable'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE tenants_client ALTER COLUMN db_port DROP NOT NULL;",
            reverse_sql="ALTER TABLE tenants_client ALTER COLUMN db_port SET NOT NULL DEFAULT 5432;",
        ),
    ]
