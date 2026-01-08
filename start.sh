#!/bin/bash

# Cloud Media Platform Backend - Startup Script

echo "==================================="
echo "Cloud Media Platform Backend"
echo "==================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "WARNING: .env file not found!"
    echo "Please copy .env.example to .env and configure your Azure credentials."
    echo ""
    echo "cp .env.example .env"
    echo ""
    exit 1
fi

# Start the application
echo ""
echo "Starting Cloud Media Platform API..."
echo "API will be available at: http://localhost:8000"
echo "Documentation: http://localhost:8000/api/docs"
echo ""
python app.py
