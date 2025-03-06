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
COPY application.py .
COPY proto proto/
COPY interfaces interfaces/
CMD ["/bin/bash", "-c", "sleep infinity"]

### Worker
FROM base AS worker
WORKDIR /app
COPY load_and_generate.py .
COPY tasks.py .
COPY worker.py .

CMD ["python", "worker.py"]