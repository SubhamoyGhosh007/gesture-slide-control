#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== Gesture Control Presenter Setup ==="

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install it first."
    exit 1
fi

echo "1. Creating virtual environment..."
python3 -m venv venv

echo "2. Activating virtual environment..."
source venv/bin/activate

echo "3. Upgrading pip..."
pip install --upgrade pip

echo "4. Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "5. Downloading Hand Landmarker models..."
python setup_models.py

echo "======================================="
echo "Setup complete!"
echo "To activate the environment in your shell, run:"
echo "  source venv/bin/activate"
echo "To run the application, run:"
echo "  python main.py"
echo "======================================="
