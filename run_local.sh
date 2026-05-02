#!/bin/bash

echo "=================================="
echo "Starting Anbar System Locally"
echo "=================================="

# Check if virtual environment exists
if [ ! -d ".venvanbar" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venvanbar
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venvanbar/bin/activate

# Install dependencies if needed
if [ ! -f ".venvanbar/installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch .venvanbar/installed
fi

# Check if database exists
if [ ! -f "db.sqlite3" ]; then
    echo "Database not found. Setting up..."
    
    # Run migrations
    echo "Running migrations..."
    DJANGO_SETTINGS_MODULE=config.settings.local python manage.py migrate
    
    # Collect static files
    echo "Collecting static files..."
    DJANGO_SETTINGS_MODULE=config.settings.local python manage.py collectstatic --noinput
    
    # Seed data
    echo "Creating test data..."
    python seed_data.py
    
    echo ""
    echo "=================================="
    echo "Database setup complete!"
    echo "=================================="
else
    echo "Database exists. Skipping setup."
fi

echo ""
echo "=================================="
echo "Test Accounts:"
echo "=================================="
echo "Superuser:  admin / admin123"
echo "Manager:    manager / manager123"
echo "Operator:   operator / operator123"
echo "Worker 1:   ali_rezaei / worker123"
echo "Worker 2:   sara_ahmadi / worker123"
echo "Worker 3:   reza_karimi / worker123"
echo "=================================="
echo ""
echo "Starting Django development server..."
echo "Access admin panel at: http://127.0.0.1:8000/admin/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="
echo ""

# Run server
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver
