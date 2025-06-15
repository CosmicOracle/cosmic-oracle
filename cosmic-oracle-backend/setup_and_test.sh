#!/bin/bash

# Setup and test script for cosmic-oracle-backend

echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setting up environment variables..."
echo "Please copy your .env file from .env.template or other .env.* files before proceeding."

echo "Running database migrations..."
flask db upgrade

echo "Seeding initial data..."
python seed_data.py

echo "Running backend tests..."
pytest --maxfail=1 --disable-warnings -q

echo "Starting backend server..."
python run.py
