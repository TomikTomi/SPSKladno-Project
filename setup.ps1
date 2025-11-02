Param()

$ErrorActionPreference = 'Stop'

Write-Host 'Setting up virtual environment and installing dependencies...'

if (-Not (Test-Path -Path './venv')) {
  Write-Host 'Creating virtual environment (venv)...'
  python -m venv venv
}

Write-Host 'Activating venv...'
. "./venv/Scripts/Activate.ps1"

Write-Host 'Upgrading pip...'
python -m pip install --upgrade pip

Write-Host 'Installing requirements...'
pip install -r requirements.txt

Write-Host 'Done. To run the app: python launcher.py'