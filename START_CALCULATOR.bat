@echo off
title Structures America - Material Takeoff Calculator
echo.
echo  =====================================================
echo   STRUCTURES AMERICA Material Takeoff Calculator
echo   Titan Carports Inc. - Conroe, TX
echo  =====================================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found. Please install Python 3.8+
    echo  Download at: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check dependencies
python -c "import tornado, openpyxl, reportlab" >nul 2>&1
if errorlevel 1 (
    echo  Installing required packages...
    pip install tornado openpyxl reportlab pillow
    echo.
)

echo  Starting calculator at http://localhost:8888
echo  Browser will open automatically...
echo  Press Ctrl+C to stop.
echo.
python app.py --port 8888
pause
