@echo off
echo ========================================
echo Telegram Bot Startup Script
echo ========================================
echo.

echo [1/3] Checking for running Python processes...
tasklist /FI "IMAGENAME eq python.exe" | find /I "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo WARNING: Python processes are running!
    echo Killing all Python processes...
    taskkill /F /IM python.exe /T
    timeout /t 2 >nul
)

tasklist /FI "IMAGENAME eq py.exe" | find /I "py.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo WARNING: py.exe processes are running!
    echo Killing all py.exe processes...
    taskkill /F /IM py.exe /T
    timeout /t 2 >nul
)

echo [2/3] Clearing webhook (if any)...
py check_webhook.py
echo.

echo [3/3] Starting the bot...
echo.
py bot.py

pause
