#!/bin/bash

# Workshop Tool Inventory System - Setup Script

echo "🔧 Workshop Tool Inventory System - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created (please edit with your configuration)"
    echo ""
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p logs media/barcodes staticfiles
echo "✓ Directories created"
echo ""

echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database configuration"
echo "2. Create PostgreSQL database: createdb workshop_inventory"
echo "3. Run migrations: python manage.py migrate"
echo "4. Create superuser: python manage.py createsuperuser"
echo "5. Run server: python manage.py runserver"
echo ""
echo "Access admin at: http://localhost:8000/admin/"
echo ""
