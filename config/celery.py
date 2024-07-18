from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks from all installed apps
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-daily-likes-summary': {
        'task': 'your_app_name.tasks.send_daily_likes_summary',
        'schedule': crontab(hour=0, minute=0),  # Executes every day at midnight
    },
}
