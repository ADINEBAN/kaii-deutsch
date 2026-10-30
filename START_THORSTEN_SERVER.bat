@echo off
setlocal enabledelayedexpansion
title WordFeather Thorsten TTS Server Launcher
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo   KHỞI ĐỘNG HỆ THỐNG MÁY CHỦ KAII DEUTSCH ^& THORSTEN TTS
echo ============================================================
echo.

:: 1. Mo port Firewall Windows 8080 va 8000
powershell -Command "New-NetFirewallRule -DisplayName 'KAII Server 8080' -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue; New-NetFirewallRule -DisplayName 'KAII TTS 8000' -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue" >nul 2>&1

:: 2. Kiem tra va khoi dong Docker Container Thorsten neu co Docker
where docker >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [1/3] Kiem tra Docker Engine...
    docker info >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        if exist "%ProgramFiles%\Docker\Docker\Docker Desktop.exe" (
            echo       Dang bat Docker Desktop...
            start "" "%ProgramFiles%\Docker\Docker\Docker Desktop.exe"
            timeout /t 10 /nobreak >nul
        )
    )
    
    docker inspect thorsten-kokoro-tts >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo [2/3] Dang bat container Thorsten TTS (port 8000)...
        docker start thorsten-kokoro-tts >nul 2>&1
    ) else (
        echo [2/3] Chua tao container Thorsten. Ban co the tao bang lenh:
        echo       docker run -d --name thorsten-kokoro-tts -p 8000:8000 -v kokoro_cache:/data/hf-cache --restart unless-stopped thorstenvoice/kokoro-tts:latest
    )
) else (
    echo [THONG BAO] May chua cai Docker -> Se dung che do Proxy va Giong may.
)

:: 3. Chay Dev Server Proxy (port 8080)
echo.
echo [3/3] Dang khoi dong Web Server ^& Safe Proxy tren port 8080...
echo ------------------------------------------------------------
echo   Dia chi ket noi tren dien thoai:
echo   👉 http://192.168.1.5:8080
echo ------------------------------------------------------------
echo   De tat server: Dong cua so nay hoac an Ctrl+C.
echo ============================================================
echo.

python dev_server.py --port 8080
pause
