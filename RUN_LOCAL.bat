@echo off
setlocal enabledelayedexpansion
title WordFeather Local Launcher
cd /d "%~dp0"

echo ======================================================================
echo   WordFeather - Thorsten-Voice Kokoro TTS Launcher
echo ======================================================================
echo.

:: ---------------------------------------------------------------------
:: 1. Check Docker Installation
:: ---------------------------------------------------------------------
where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 goto err_no_docker

:: ---------------------------------------------------------------------
:: 2. Check if Docker Daemon is Running
:: ---------------------------------------------------------------------
echo [1/5] Checking Docker daemon status...
docker info >nul 2>&1
if %ERRORLEVEL% EQU 0 goto docker_ready

echo [INFO] Docker daemon is not responding. Checking for Docker Desktop...
set "DOCKER_DESKTOP_EXE=%ProgramFiles%\Docker\Docker\Docker Desktop.exe"
if not exist "%DOCKER_DESKTOP_EXE%" goto err_docker_not_running

echo [INFO] Starting Docker Desktop application...
start "" "%DOCKER_DESKTOP_EXE%"
echo [INFO] Waiting for Docker daemon to become ready - up to 90 seconds...

set /a DOCKER_WAIT=0
:wait_docker_loop
timeout /t 3 /nobreak >nul 2>&1 || ping -n 4 127.0.0.1 >nul
docker info >nul 2>&1
if %ERRORLEVEL% EQU 0 goto docker_ready
set /a DOCKER_WAIT+=3
if !DOCKER_WAIT! GEQ 90 goto err_docker_timeout
echo        Waiting for Docker Engine... !DOCKER_WAIT!s of 90s
goto wait_docker_loop

:docker_ready
echo [OK] Docker daemon is running.
echo.

:: ---------------------------------------------------------------------
:: 3. Check and Start thorsten-kokoro-tts Container
:: ---------------------------------------------------------------------
echo [2/5] Checking Thorsten-Voice Kokoro container: thorsten-kokoro-tts...
docker inspect thorsten-kokoro-tts >nul 2>&1
if %ERRORLEVEL% NEQ 0 goto err_no_container

:: Check if container is running
docker inspect -f "{{.State.Running}}" thorsten-kokoro-tts > __status.tmp 2>nul
set "CONTAINER_RUNNING="
if exist __status.tmp (
    set /p CONTAINER_RUNNING=<__status.tmp
    del /f /q __status.tmp >nul 2>&1
)

if /i "%CONTAINER_RUNNING%"=="true" goto container_already_running

echo [INFO] Container 'thorsten-kokoro-tts' is stopped. Starting it now...
docker start thorsten-kokoro-tts >nul 2>&1
if %ERRORLEVEL% NEQ 0 goto err_container_start_failed
echo [OK] Container started successfully.
goto check_tts_health

:container_already_running
echo [OK] Container 'thorsten-kokoro-tts' is running.

:check_tts_health
echo.

:: ---------------------------------------------------------------------
:: 4. Poll TTS Health Endpoint (http://127.0.0.1:8000/health)
:: ---------------------------------------------------------------------
echo [3/5] Verifying TTS model health at http://127.0.0.1:8000/health...
set /a HEALTH_WAIT=0

:wait_tts_loop
curl.exe -s -f http://127.0.0.1:8000/health >nul 2>&1
if %ERRORLEVEL% EQU 0 goto tts_ready

set /a HEALTH_WAIT+=3
if !HEALTH_WAIT! GEQ 120 goto tts_timeout
echo        Waiting for model initialization... !HEALTH_WAIT!s of 120s
timeout /t 3 /nobreak >nul 2>&1 || ping -n 4 127.0.0.1 >nul
goto wait_tts_loop

:tts_timeout
echo [WARNING] TTS health check timed out after 120 seconds.
echo           The server may still be downloading model weights.
echo           WordFeather will continue and fall back to browser speech if necessary.
goto check_web_server

:tts_ready
echo [OK] Thorsten-Voice TTS service is healthy and ready!

:check_web_server
echo.

:: ---------------------------------------------------------------------
:: 5. Start WordFeather Local Development Server & Safe Proxy
:: ---------------------------------------------------------------------
echo [4/5] Checking WordFeather web server on port 8080...
curl.exe -s -f http://127.0.0.1:8080/api/tts/health >nul 2>&1
if %ERRORLEVEL% EQU 0 goto server_already_running

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 goto start_python_server

where node >nul 2>&1
if %ERRORLEVEL% EQU 0 goto start_node_server

goto err_no_runtime

:server_already_running
echo [OK] WordFeather dev server is already running on http://localhost:8080/
goto wait_for_site

:start_python_server
echo [INFO] Launching WordFeather dev server with Python: dev_server.py
start "WordFeather Dev Server" python dev_server.py
goto wait_for_site

:start_node_server
echo [INFO] Python not found. Launching WordFeather dev server with Node.js: dev_server.js
start "WordFeather Dev Server" node dev_server.js
goto wait_for_site

:: ---------------------------------------------------------------------
:: 6. Wait for Website and Open Browser
:: ---------------------------------------------------------------------
:wait_for_site
echo [5/5] Waiting for website to respond at http://localhost:8080/...
set /a SITE_WAIT=0

:wait_site_loop
curl.exe -s -f http://127.0.0.1:8080/api/tts/health >nul 2>&1
if %ERRORLEVEL% EQU 0 goto site_ready
timeout /t 1 /nobreak >nul 2>&1 || ping -n 2 127.0.0.1 >nul
set /a SITE_WAIT+=1
if !SITE_WAIT! GEQ 15 goto site_ready
goto wait_site_loop

:site_ready
echo [OK] WordFeather website is live!
echo.
echo ======================================================================
echo   WordFeather is ready!
echo ======================================================================
echo   Website URL:   http://localhost:8080/
echo   Mobile App:    http://[IP-cua-may-tinh]:8080/m (Realme GT Neo 2T)
echo   TTS Backend:   http://127.0.0.1:8000/ - Thorsten-Voice Kokoro
echo   Dev Proxy:     http://localhost:8080/api/tts
echo   Container:     thorsten-kokoro-tts
echo.
echo   To stop the website server, run: STOP_LOCAL.bat
echo ======================================================================
echo.

start http://localhost:8080/

echo Launcher finished. Leave this window open, or close it anytime.
pause
exit /b 0

:: ---------------------------------------------------------------------
:: Error Handlers
:: ---------------------------------------------------------------------
:err_no_docker
echo.
echo ======================================================================
echo [ERROR] Docker command line tool was not found in PATH!
echo ======================================================================
echo Please install Docker Desktop from:
echo   https://www.docker.com/products/docker-desktop
echo and ensure it is running.
echo.
goto pause_and_exit

:err_docker_not_running
echo.
echo ======================================================================
echo [ERROR] Docker daemon is not running and Docker Desktop was not found!
echo ======================================================================
echo Please start Docker Desktop or your Docker service manually.
echo.
goto pause_and_exit

:err_docker_timeout
echo.
echo ======================================================================
echo [ERROR] Docker Desktop did not become ready within 90 seconds!
echo ======================================================================
echo Please open Docker Desktop manually, wait until the engine is running,
echo and run RUN_LOCAL.bat again.
echo.
goto pause_and_exit

:err_no_container
echo.
echo ======================================================================
echo [ERROR] Docker container 'thorsten-kokoro-tts' does not exist!
echo ======================================================================
echo To create and initialize the Thorsten-Voice container, run this command:
echo.
echo   docker run -d --name thorsten-kokoro-tts -p 8000:8000 -v kokoro_cache:/data/hf-cache --restart unless-stopped thorstenvoice/kokoro-tts:latest
echo.
echo After creating the container, re-run RUN_LOCAL.bat.
echo ======================================================================
echo.
goto pause_and_exit

:err_container_start_failed
echo.
echo ======================================================================
echo [ERROR] Failed to start container 'thorsten-kokoro-tts'!
echo ======================================================================
echo Run 'docker logs thorsten-kokoro-tts' to check the container logs.
echo.
goto pause_and_exit

:err_no_runtime
echo.
echo ======================================================================
echo [ERROR] Neither Python 3 nor Node.js was found in PATH!
echo ======================================================================
echo Please install Python 3.8+ (recommended) or Node.js 18+ to run the local server.
echo.
goto pause_and_exit

:pause_and_exit
echo Press any key to close this window...
pause >nul
exit /b 1
