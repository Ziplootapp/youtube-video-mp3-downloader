@echo off
title ZipLoot YT Downloader — 1-Click Deployment (Windows)
echo ========================================================
echo   ZipLoot YouTube Downloader 1-Click Deployment (Windows)
echo ========================================================
echo.

:: Detect Python executable
set PY_CMD=python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PY_CMD=py
    ) else (
        echo [ERROR] Python is not installed or not in your system PATH!
        echo Please install Python (3.8 or newer) from https://python.org before running this script.
        pause
        exit /b 1
    )
)

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo [INFO] Creating Python Virtual Environment (venv)...
    %PY_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
)

:: Activate virtual environment and install dependencies
echo [INFO] Activating virtual environment...
call venv\Scripts\activate

echo [INFO] Installing required dependencies (Flask, yt-dlp, imageio-ffmpeg)...
python -m pip install -r requirements.txt --pre
if %errorlevel% neq 0 (
    echo [ERROR] Dependency installation failed!
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   [SUCCESS] Deployment complete! Launching server...
echo   Open: http://localhost:5000 in your browser.
echo ========================================================
echo.

start http://localhost:5000
python app.py
pause
