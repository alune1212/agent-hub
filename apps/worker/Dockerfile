FROM python:3.14-slim

WORKDIR /workspace

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY libs ./libs
COPY apps/api/pyproject.toml ./apps/api/pyproject.toml
COPY apps/worker ./apps/worker

RUN uv sync

CMD ["uv", "run", "--project", "apps/worker", "celery", "-A", "worker.celery_app:celery_app", "worker", "--loglevel=INFO", "--pool=solo"]
