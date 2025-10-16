from django.apps import AppConfig
from django.contrib.auth import get_user_model

class PharmacyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pharmacy'

    def ready(self):
        # Import inside ready to avoid AppRegistryNotReady issues
        from django.conf import settings
        User = get_user_model()

        # Admin credentials (change these for production)
        admin_username = "admin"
        admin_email = "admin@example.com"
        admin_password = "Admin@123"  # Change this before production!

        # Check if admin exists
        if not User.objects.filter(username=admin_username, role="admin").exists():
            print("Creating default admin user...")
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                role="admin"
            )
