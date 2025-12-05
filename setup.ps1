# Screenshot to Code - Quick Setup Script
# Run this script after installing Python and MySQL

Write-Host "Screenshot to Code - Setup Script" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Check Python version
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.10 or higher." -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check if .env exists
if (Test-Path ".env") {
    Write-Host "✓ .env file exists" -ForegroundColor Green
} else {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host "⚠ Please edit .env file with your configuration!" -ForegroundColor Yellow
}

# Create upload directory
Write-Host "Creating upload directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "app\static\uploads" -Force | Out-Null
Write-Host "✓ Upload directory created" -ForegroundColor Green

Write-Host ""
Write-Host "=================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your configuration" -ForegroundColor White
Write-Host "2. Create MySQL database:" -ForegroundColor White
Write-Host "   CREATE DATABASE screenshot_to_code;" -ForegroundColor Cyan
Write-Host "3. Run database migrations:" -ForegroundColor White
Write-Host "   flask db init" -ForegroundColor Cyan
Write-Host "   flask db migrate -m 'Initial migration'" -ForegroundColor Cyan
Write-Host "   flask db upgrade" -ForegroundColor Cyan
Write-Host "   flask seed_packages" -ForegroundColor Cyan
Write-Host "4. Start the application:" -ForegroundColor White
Write-Host "   python app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "For detailed instructions, see docs/setup.md" -ForegroundColor Yellow
