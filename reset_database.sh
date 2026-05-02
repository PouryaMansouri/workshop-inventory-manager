#!/bin/bash

echo "=================================="
echo "Resetting Database"
echo "=================================="

# Activate virtual environment
source .venvanbar/bin/activate

# Remove old database
if [ -f "db.sqlite3" ]; then
    echo "Removing old database..."
    rm db.sqlite3
fi

# Remove old migrations (optional)
read -p "Do you want to remove old migrations? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing migrations..."
    find apps -path "*/migrations/*.py" -not -name "__init__.py" -delete
    find apps -path "*/migrations/*.pyc" -delete
fi

# Run migrations
echo "Running migrations..."
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py makemigrations
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py migrate

# Collect static files
echo "Collecting static files..."
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py collectstatic --noinput

# Seed data
echo "Creating test data..."
python seed_data.py

echo ""
echo "=================================="
echo "Database reset complete!"
echo "=================================="
echo ""
echo "Test Accounts:"
echo "Superuser:  admin / admin123"
echo "Manager:    manager / manager123"
echo "Operator:   operator / operator123"
echo "Workers:    ali_rezaei, sara_ahmadi, reza_karimi / worker123"
echo "=================================="
