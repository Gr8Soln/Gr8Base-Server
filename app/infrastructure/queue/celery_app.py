from celery import Celery

from app.infrastructure.config.settings import settings

celery_app = Celery(
    "ai_ats",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.adapters.queue.tasks.resume_tasks",
        "app.adapters.queue.tasks.scoring_tasks",
        "app.adapters.queue.tasks.generation_tasks",
        "app.adapters.queue.tasks.embedding_tasks",
        "app.adapters.queue.tasks.analytics_tasks",
        "app.adapters.queue.tasks.render_tasks",
    ],
)

celery_app.config_from_object("app.infrastructure.queue.celery_config")
