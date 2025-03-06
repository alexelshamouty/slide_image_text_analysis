FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/tmp

FROM base AS application
COPY load_and_generate.py .
COPY tasks.py .
COPY application.py .
COPY proto .
COPY interfaces .

CMD ["/bin/bash", "-c", "sleep infinity"]

FROM base AS worker
COPY load_and_generate.py .
COPY tasks.py .
COPY worker.py .

CMD ["python", "worker.py"]