#!/usr/bin/env bash
set -euo pipefail

echo "Setting up virtual environment and installing dependencies..."

if [ ! -d "venv" ]; then
  echo "Creating virtual environment (venv)..."
  if command -v python3 >/dev/null 2>&1; then
    python3 -m venv venv
  else
    python -m venv venv
  fi
fi

echo "Activating venv..."
source venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing requirements..."
pip install -r requirements.txt

echo "Done. To run the app: python launcher.py"