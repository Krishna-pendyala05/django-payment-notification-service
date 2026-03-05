import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Read config from Django settings, using CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks in all registered Django apps
app.autodiscover_tasks()
