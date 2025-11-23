from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError, InterfaceError


class PharmacyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pharmacy'

    def ready(self):
        from django.conf import settings
        from django.db import connection

        try:
            # Don't run during migrations or before DB is ready
            if connection.introspection.table_names() and 'pharmacy_user' in connection.introspection.table_names():
                User = get_user_model()

                admin_username = "admin"
                admin_email = "admin@example.com"
                admin_password = "admin123"

                if not User.objects.filter(username=admin_username, role="admin").exists():
                    print("Creating default admin user...")
                    User.objects.create_superuser(
                        username=admin_username,
                        email=admin_email,
                        password=admin_password,
                        role="admin"
                    )
                # else:
                    # print("Admin user already exists ✔")
            else:
                print("Skipping admin creation — database tables not ready yet.")
        except (OperationalError, ProgrammingError, InterfaceError):
            # Happens if DB is locked or not ready (like on first run)
            print("Database not ready, skipping admin creation.")
            return
