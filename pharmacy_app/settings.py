import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-linfk6dl#^npscg$gt^70^xi9nx8e4duj=hp+@q2!38ouw84)%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*']






# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'pharmacy', # Custom user model and authentication
    'medicine', # For medicine management
    'supplier', # For supplier management
    'billing', # For billing management
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pharmacy_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'pharmacy.context_processors.company_info',
            ],
        },
        
    },
]

WSGI_APPLICATION = 'pharmacy_app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'superadmin',
        'HOST': 'localhost',   # or your server IP
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # ✅ Required for Render

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGIN_URL = '/login/'       # where @login_required sends users
LOGIN_REDIRECT_URL = '/dashboard/'   # default redirect after login
LOGOUT_REDIRECT_URL = '/login/'


AUTHENTICATION_BACKENDS = ['pharmacy.backends.CustomUserBackend']
AUTH_USER_MODEL = 'pharmacy.User'

# Email settings (configure properly in production)
# # SMTP settings for real email sending
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Switch to SMTP for real email sending
# EMAIL_HOST = 'smtp.gmail.com'  # For Gmail, change to your provider's SMTP server
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'danfetest@gmail.com'  # Your email
# EMAIL_HOST_PASSWORD = 'uksc hffl crrg fwwy'  # Gmail App Password
# DEFAULT_FROM_EMAIL = 'danfetest@gmail.com'
ADMIN_EMAIL = 'bigyanbhaila98@gmail.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.easedpharma.com'   # Example: mail.easedpharma.com
EMAIL_PORT = 465
EMAIL_USE_SSL = True

EMAIL_HOST_USER = 'noreply@easedpharma.com'
EMAIL_HOST_PASSWORD = '@easedpharma0010PMS'

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
