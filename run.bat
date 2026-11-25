@echo off
title Manav Rachna Smart Campus Route Optimizer - DAA Project
cls
echo =================================================================
echo   MANAV RACHNA SMART CAMPUS ROUTE OPTIMIZER - DAA LAUNCHER       
echo =================================================================
echo [1/2] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

echo [2/2] Launching FastAPI Web Application...
start http://127.0.0.1:8000
python main.py --host 127.0.0.1 --port 8000
pause
