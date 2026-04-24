from .base import *
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': '5432',
    }
}

SECURE_SSL_REDIRECT = False  # Disabled for development/testing
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_SECURE = False  # Disabled for development/testing
CSRF_COOKIE_SECURE = False  # Disabled for development/testing
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:65462",
    "http://localhost:65462",
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email configuration - Mailjet SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'in-v3.mailjet.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('MAILJET_API_KEY')
EMAIL_HOST_PASSWORD = config('MAILJET_SECRET_KEY')
DEFAULT_FROM_EMAIL = config('MAILJET_FROM_EMAIL')
