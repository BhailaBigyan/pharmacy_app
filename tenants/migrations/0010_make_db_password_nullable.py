# Generated manually to make db_password nullable

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0009_client_db_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='db_password',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
