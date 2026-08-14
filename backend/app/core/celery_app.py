"""Celery application configuration for asynchronous OSINT collection tasks."""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "osintx_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.COLLECTOR_TIMEOUT_SECONDS + 30,
    task_soft_time_limit=settings.COLLECTOR_TIMEOUT_SECONDS,
    worker_concurrency=4,
    worker_prefetch_multiplier=1,
)
