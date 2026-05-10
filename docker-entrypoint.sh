#!/bin/bash
set -e

echo "Starting Workshop Tool Inventory System..."

# Wait for database to be ready
echo "Waiting for database..."
python - <<'PY'
import socket
import time
import os

host = os.getenv("POSTGRES_HOST", "db")
port = int(os.getenv("POSTGRES_PORT", "5432"))

while True:
    try:
        with socket.create_connection((host, port), timeout=1):
            break
    except OSError:
        time.sleep(0.2)
PY
echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create logs directory
mkdir -p /app/logs

echo "Starting Gunicorn..."
exec "$@"
