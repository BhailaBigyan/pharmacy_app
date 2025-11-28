# Generated manually to fix missing created_on column

from django.db import migrations, models
from django.utils import timezone


def set_created_on_default(apps, schema_editor):
    """Set default created_on for existing records"""
    Client = apps.get_model('tenants', 'Client')
    for client in Client.objects.all():
        if not client.created_on:
            client.created_on = timezone.now().date()
            client.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='created_on',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.RunPython(set_created_on_default, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='client',
            name='created_on',
            field=models.DateField(auto_now_add=True),
        ),
    ]
