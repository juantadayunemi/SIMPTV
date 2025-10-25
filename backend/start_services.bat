@echo off
echo ========================================
echo TrafiSmart - Iniciando Servicios
echo ========================================

echo.
echo [1/4] Verificando Redis...
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Redis ya está corriendo
) else (
    echo Iniciando Redis...
    start "Redis Server" redis-server
    timeout /t 2 /nobreak >nul
)

echo.
echo [2/4] Iniciando Celery Worker...
start "Celery Worker" cmd /k "cd /d %~dp0 && celery -A config worker --loglevel=info --pool=solo"
timeout /t 3 /nobreak >nul

echo.
echo [3/4] Iniciando Daphne (WebSocket)...
start "Daphne WebSocket" cmd /k "cd /d %~dp0 && daphne -b 0.0.0.0 -p 8001 config.asgi:application"
timeout /t 2 /nobreak >nul

echo.
echo [4/4] Iniciando Django...
start "Django Server" cmd /k "cd /d %~dp0 && python manage.py runserver"

echo.
echo ========================================
echo Todos los servicios iniciados!
echo ========================================
echo.
echo Django:    http://localhost:8000
echo WebSocket: ws://localhost:8001
echo Redis:     localhost:6379
echo.
pause