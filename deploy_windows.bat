@echo off
title ZipLoot YT Downloader — 1-Click Deployment (Windows)
echo ========================================================
echo   ZipLoot YouTube Downloader 1-Click Deployment (Windows)
echo ========================================================
echo.

set PY_CMD=python
python --version >nul 2>&1
if %errorlevel%==0 goto FOUND_PY

set PY_CMD=py
py --version >nul 2>&1
if %errorlevel%==0 goto FOUND_PY

echo [ERROR] Python is not installed or not in system PATH!
echo Please install Python 3.8 or newer before running this script.
pause
exit /b 1

:FOUND_PY
if not exist venv (
    echo [INFO] Creating Python Virtual Environment...
    %PY_CMD% -m venv venv
)

if not exist venv\Scripts\activate.bat (
    echo [ERROR] Virtual environment creation failed!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo [INFO] Installing required dependencies...
python -m pip install -r requirements.txt --pre

echo.
echo ========================================================
echo   [SUCCESS] Launching ZipLoot YouTube Downloader...
echo ========================================================
echo.

start http://localhost:5000
python app.py
pause
