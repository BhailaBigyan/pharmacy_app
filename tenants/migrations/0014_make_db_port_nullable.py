# Generated manually to make db_port nullable

from django.db import migrations, models


def make_db_port_nullable(apps, schema_editor):
    """Make db_port nullable using raw SQL"""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("ALTER TABLE tenants_client ALTER COLUMN db_port DROP NOT NULL;")


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0013_client_db_port'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE tenants_client ALTER COLUMN db_port DROP NOT NULL;",
            reverse_sql="ALTER TABLE tenants_client ALTER COLUMN db_port SET NOT NULL;",
        ),
        migrations.AlterField(
            model_name='client',
            name='db_port',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
