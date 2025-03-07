FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /app/tmp

### Application
FROM base AS application
WORKDIR /app
COPY load_and_generate.py .
COPY tasks.py .
COPY api.py .
COPY log_config.py .
COPY application.py .
COPY interfaces interfaces/
CMD ["python", "application.py"]

### Backend
FROM base AS backend
WORKDIR /app
COPY backend.py .
COPY log_config.py .
COPY interfaces interfaces/
CMD ["fastapi","dev", "backend.py"]

### Worker
FROM base AS worker
WORKDIR /app
COPY load_and_generate.py .
COPY tasks.py .
COPY worker.py .
COPY log_config.py .
CMD ["python", "worker.py"]