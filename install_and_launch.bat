@echo off
REM SoloHeart Install and Launch Script (Windows)
REM =============================================
REM One-command setup and launch for SoloHeart

echo 🎲 SoloHeart Installer
echo ======================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo    Please install Python 3.9 or higher and try again
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python version: %PYTHON_VERSION%

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

echo ✅ Installation complete!
echo.
echo 🚀 Launching SoloHeart...
echo    Press Ctrl+C to stop the server
echo.

REM Launch SoloHeart
python launch_soloheart.py

pause 