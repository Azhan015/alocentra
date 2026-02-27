import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alocentra.settings.development')

app = Celery('alocentra')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
