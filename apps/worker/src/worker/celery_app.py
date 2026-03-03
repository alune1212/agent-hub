from __future__ import annotations

from celery import Celery

from worker.config import get_settings

settings = get_settings()

celery_app = Celery("internal_worker", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    timezone="Asia/Shanghai",
    enable_utc=False,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    beat_schedule={
        "consume-outbox-every-5-min": {
            "task": "worker.tasks.consume_outbox",
            "schedule": 300,
        },
        "daily-reporting-reconcile": {
            "task": "worker.tasks.daily_reconcile",
            "schedule": 86400,
        },
    },
)

celery_app.autodiscover_tasks(["worker"])
