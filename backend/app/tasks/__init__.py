"""Celery tasks package for background job processing."""

from app.tasks.collector_tasks import run_collector_job_task

__all__ = ["run_collector_job_task"]
