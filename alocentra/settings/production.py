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
