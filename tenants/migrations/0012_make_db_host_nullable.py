# Generated manually to make db_host nullable

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0010_make_db_password_nullable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='db_host',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]

