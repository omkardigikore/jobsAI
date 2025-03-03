# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Set Python path to include the current directory
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/logs /app/temp /app/tasks /app/bot/handlers /app/utils /app/ai/agents

# Create empty __init__.py files in each directory to make them proper packages
RUN touch /app/__init__.py \
    && touch /app/bot/__init__.py \
    && touch /app/bot/handlers/__init__.py \
    && touch /app/utils/__init__.py \
    && touch /app/ai/__init__.py \
    && touch /app/ai/agents/__init__.py

# Copy application code
COPY . .

# Default command
CMD ["uvicorn", "config.asgi:app", "--host", "0.0.0.0", "--port", "8000"]