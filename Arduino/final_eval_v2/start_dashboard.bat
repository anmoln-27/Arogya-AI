@echo off
title Smart-ASHA Pro Web Dashboard
cd /d "%~dp0"
echo ========================================================
echo   SMART-ASHA PRO: WEB DASHBOARD & ZERO-APP EXPORT
echo ========================================================
echo.
echo [1/2] Starting local secure web server on port 8000...
echo [2/2] Opening Chrome at http://localhost:8000/web_dashboard.html ...
echo.
echo * Note: Running on localhost unlocks full Web-Bluetooth and Web-Serial!
echo.

start "" "http://localhost:8000/web_dashboard.html"
python -m http.server 8000

pause
