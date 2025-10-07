import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "risk_detector.settings")

app = Celery("risk_detector")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
