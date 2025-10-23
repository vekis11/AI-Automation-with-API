@echo off
echo Installing API Anomaly Detection System Dependencies...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Creating necessary directories...
mkdir models 2>nul
mkdir logs 2>nul
mkdir data 2>nul

echo.
echo Installation completed successfully!
echo.
echo To start the service, run:
echo   python main.py
echo.
echo Or use the Makefile commands:
echo   make run
echo.
pause
