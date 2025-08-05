# celery_app.py

"""
Celery Application Configuration

This file initializes the Celery application used for handling background tasks (e.g., sending emails).
The configuration is loaded from the `settings.CELERY` dictionary defined in the application's config.

- The Celery app is named "tasks"
- Settings include broker URL, backend, task serialization options, etc.
"""


from celery import Celery
from core.config import settings

app = Celery("tasks")

# טוען את ההגדרות מתוך הקובץ config.py
app.conf.update(settings.CELERY)
