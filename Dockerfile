FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /app/tmp

### Backend
FROM base AS backend
WORKDIR /app
COPY utils/ utils/
COPY backend/ backend/
COPY interfaces/ interfaces/
ENV PYTHONPATH=/app
CMD ["python", "backend/server.py"]

### API
FROM base AS api
WORKDIR /app
COPY webapi/ webapi/
COPY utils/ utils/
COPY interfaces/ interfaces/
ENV PYTHONPATH=/app
CMD ["uvicorn", "webapi.webapi:app", "--host", "0.0.0.0", "--reload"]

### Worker
FROM base AS worker
WORKDIR /app
COPY utils/ utils/
COPY backend/ backend/
ENV PYTHONPATH=/app
CMD ["python", "backend/worker.py"]