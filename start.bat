@echo off
REM Cloud Media Platform Backend - Startup Script (Windows)

echo ===================================
echo Cloud Media Platform Backend
echo ===================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and configure your Azure credentials.
    echo.
    echo copy .env.example .env
    echo.
    exit /b 1
)

REM Start the application
echo.
echo Starting Cloud Media Platform API...
echo API will be available at: http://localhost:8000
echo Documentation: http://localhost:8000/api/docs
echo.
python main.py
