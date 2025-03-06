FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for temporary files
RUN mkdir -p /app/tmp

# Application image
FROM base AS application
COPY load_and_generate.py .
COPY tasks.py .

CMD ["/bin/bash", "-c", "sleep infinity"]

# Worker image
FROM base AS worker
COPY load_and_generate.py .
COPY tasks.py .
COPY worker.py .

CMD ["python", "worker.py"]