#!/bin/bash

# Change to the server directory
cd "$(dirname "$0")"

# Detect Python version
if command -v python3 &>/dev/null; then
  PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
  PYTHON_CMD="python"
else
  echo "Error: Python not found. Please install Python 3.x"
  exit 1
fi

# Install required dependencies if not already installed
echo "Checking and installing dependencies..."
$PYTHON_CMD -m pip install flask flask-cors google-cloud-storage

# Run the server
echo "Starting server on port 3001..."
$PYTHON_CMD upload.py 