#!/bin/bash
set -e

echo "Starting Workshop Tool Inventory System..."

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
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
