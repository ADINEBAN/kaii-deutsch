@echo off
setlocal
title WordFeather Local Stopper
cd /d "%~dp0"

echo ======================================================================
echo   WordFeather - Local Server Stopper
echo ======================================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop_server.ps1"

echo.
echo ======================================================================
echo Press any key to close this window...
pause >nul
exit /b 0
