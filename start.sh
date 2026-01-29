#!/bin/bash

echo "======================================"
echo " Starting Mines Bot"
echo "======================================"

# Stop if any command fails
set -e

# Check Python version
PYTHON_VERSION=$(python --version 2>&1)
echo "Using $PYTHON_VERSION"

# Optional: activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the bot
echo "Starting bot..."
python run.py
