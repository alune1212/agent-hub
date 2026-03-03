FROM python:3.14-slim

WORKDIR /workspace

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY libs ./libs
COPY apps/api ./apps/api
COPY apps/worker/pyproject.toml ./apps/worker/pyproject.toml

RUN uv sync

EXPOSE 8000

CMD ["uv", "run", "--project", "apps/api", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
