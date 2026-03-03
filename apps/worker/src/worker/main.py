from __future__ import annotations

from worker.celery_app import celery_app


def run_worker() -> None:
    celery_app.worker_main([
        "worker",
        "--loglevel=INFO",
        "--pool=solo",
    ])


def run_beat() -> None:
    celery_app.start([
        "celery",
        "beat",
        "--loglevel=INFO",
    ])
