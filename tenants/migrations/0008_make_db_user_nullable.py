# Generated manually to make db_user nullable

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0007_client_db_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='db_user',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
