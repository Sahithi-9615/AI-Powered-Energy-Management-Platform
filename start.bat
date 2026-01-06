@echo off
REM Smart Energy Platform - Windows Startup Script

echo ================================
echo Smart Energy Analysis Platform
echo ================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/Update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if model exists
if not exist "model.pkl" (
    echo WARNING: model.pkl not found!
    echo Please ensure your trained model is in the project directory.
)

REM Check for .env file
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Creating from .env.example...
    copy .env.example .env
    echo Please edit .env with your API keys.
)

echo.
echo Setup complete!
echo.
echo Starting Flask server...
echo Access the application at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the Flask app
python app.py

pause
