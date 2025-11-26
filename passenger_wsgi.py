import sys
import os

# 1. Add your project path
PROJECT_PATH = '/home2/easedpha/public_html/pharmacy_app'
sys.path.insert(0, PROJECT_PATH)

# 2. If you use a virtual environment, uncomment these lines and adjust path
#ENV_PATH = '/home2/easedpha/public_html/pharmacy_app/venv/lib/python3.*/site-packages'
#sys.path.insert(0, VENV_PATH)

# 3. Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'pharmacy_app.settings'  # replace 'pharmacy_app.settings' with your actual settings module path

# 4. Setup WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()