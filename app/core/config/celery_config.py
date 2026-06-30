from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings
from app.infrastructure.workers import *  # noqa: F401, F403

settings = get_settings()


# Create Celery app
celery_app = Celery(
    f"{str(settings.APP_NAME).lower()}-celery",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.infrastructure.workers"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Task schedule (beat schedule)
celery_app.conf.beat_schedule = {
    "cleanup-old-notifications": {
        "task": "app.infrastructure.workers.notification_tasks.cleanup_old_notification_logs_task",
        "schedule": crontab(hour=2, minute=0),  # daily at 02:00 UTC
    }
}

