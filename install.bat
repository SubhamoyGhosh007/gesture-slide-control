@echo off
echo === Gesture Control Presenter Setup (Windows) ===

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in system PATH.
    pause
    exit /b 1
)

echo 1. Creating virtual environment...
python -m venv venv

echo 2. Activating virtual environment...
call venv\Scripts\activate.bat

echo 3. Upgrading pip...
python -m pip install --upgrade pip

echo 4. Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo 5. Downloading Hand Landmarker models...
python setup_models.py

echo =======================================
echo Setup complete!
echo To run the application, activate the venv and execute main.py:
echo   venv\Scripts\activate
echo   python main.py
echo =======================================
pause
