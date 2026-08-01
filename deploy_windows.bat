@echo off
title ZipLoot YT Downloader - 1-Click Deployment
echo ========================================================
echo   ZipLoot YouTube Downloader 1-Click Deployment
echo ========================================================
echo.

set PY_CMD=python
python --version >nul 2>&1
if %errorlevel%==0 goto FOUND_PY

set PY_CMD=py
py --version >nul 2>&1
if %errorlevel%==0 goto FOUND_PY

echo [INFO] Python not found in PATH! Attempting automatic installation via Winget...
winget install --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
if %errorlevel%==0 (
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
    set PY_CMD=python
    goto FOUND_PY
)

echo [ERROR] Python is required to run ZipLoot YT Downloader.
echo Please install Python from https://www.python.org/downloads/ (check 'Add to PATH').
pause
exit /b 1

:FOUND_PY
echo [INFO] Python detected successfully.

:: Try Virtual Environment first, fallback to direct pip if venv fails
if not exist venv (
    echo [INFO] Creating Python environment...
    %PY_CMD% -m venv venv >nul 2>&1
)

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [WARN] Virtual environment skipped, using direct Python...
)

echo [INFO] Installing required dependencies (yt-dlp, flask, etc.)...
%PY_CMD% -m pip install --upgrade pip >nul 2>&1
%PY_CMD% -m pip install -r requirements.txt --no-warn-script-location

echo.
echo ========================================================
echo   [SUCCESS] Launching ZipLoot YouTube Downloader...
echo ========================================================
echo.

start http://localhost:5000
%PY_CMD% app.py
pause
