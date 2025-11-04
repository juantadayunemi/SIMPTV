# Script para iniciar todos los servicios de TrafiSmart
# Autor: TrafiSmart Backend Team
# Fecha: 2025-11-02

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   TrafiSmart - Iniciando Todos los Servicios" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si estamos en el directorio correcto
$currentDir = Get-Location
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Error: Debes ejecutar este script desde el directorio backend/" -ForegroundColor Red
    Write-Host "   Ejecuta: cd backend" -ForegroundColor Yellow
    exit 1
}

Write-Host "📁 Directorio actual: $currentDir" -ForegroundColor Green
Write-Host ""

# 1. Verificar Redis
Write-Host "🔍 Verificando Redis..." -ForegroundColor Yellow
try {
    $redisTest = redis-cli ping 2>&1
    if ($redisTest -eq "PONG") {
        Write-Host "✅ Redis está corriendo correctamente" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Redis no responde correctamente" -ForegroundColor Yellow
        Write-Host "   Respuesta: $redisTest" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Redis no está corriendo" -ForegroundColor Red
    Write-Host "   Inicia Redis en otra terminal con:" -ForegroundColor Yellow
    Write-Host "   cd redis" -ForegroundColor White
    Write-Host "   .\redis-server.exe redis.windows.conf" -ForegroundColor White
    Write-Host ""
}

# 2. Verificar entorno virtual
Write-Host ""
Write-Host "🔍 Verificando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "✅ Entorno virtual encontrado" -ForegroundColor Green
    $pythonPath = "venv\Scripts\python.exe"
} else {
    Write-Host "❌ Entorno virtual no encontrado" -ForegroundColor Red
    Write-Host "   Crea uno con: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# 3. Verificar dependencias instaladas
Write-Host ""
Write-Host "🔍 Verificando dependencias..." -ForegroundColor Yellow
$celeryCheck = & $pythonPath -c "import celery; print('OK')" 2>&1
$djangoCheck = & $pythonPath -c "import django; print('OK')" 2>&1
$channelsCheck = & $pythonPath -c "import channels; print('OK')" 2>&1

if ($celeryCheck -eq "OK" -and $djangoCheck -eq "OK" -and $channelsCheck -eq "OK") {
    Write-Host "✅ Todas las dependencias principales están instaladas" -ForegroundColor Green
} else {
    Write-Host "⚠️  Algunas dependencias faltan:" -ForegroundColor Yellow
    if ($celeryCheck -ne "OK") { Write-Host "   - Celery: Falta" -ForegroundColor Red }
    if ($djangoCheck -ne "OK") { Write-Host "   - Django: Falta" -ForegroundColor Red }
    if ($channelsCheck -ne "OK") { Write-Host "   - Channels: Falta" -ForegroundColor Red }
    Write-Host ""
    Write-Host "   Instala con: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# 4. Mostrar servicios que deben estar corriendo
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Servicios Necesarios" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Para que el sistema funcione correctamente, necesitas 4 terminales:" -ForegroundColor White
Write-Host ""

Write-Host "Terminal 1 - Redis (Puerto 6379):" -ForegroundColor Yellow
Write-Host "   cd redis" -ForegroundColor White
Write-Host "   .\redis-server.exe redis.windows.conf" -ForegroundColor White
Write-Host ""

Write-Host "Terminal 2 - Celery Worker (Procesamiento de tareas):" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   venv\Scripts\activate" -ForegroundColor White
Write-Host "   celery -A config worker --loglevel=info --pool=solo" -ForegroundColor White
Write-Host ""

Write-Host "Terminal 3 - Daphne (WebSocket - Puerto 8001):" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   venv\Scripts\activate" -ForegroundColor White
Write-Host "   daphne -b 0.0.0.0 -p 8001 config.asgi:application" -ForegroundColor White
Write-Host ""

Write-Host "Terminal 4 - Django (API REST - Puerto 8000):" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   venv\Scripts\activate" -ForegroundColor White
Write-Host "   python manage.py runserver" -ForegroundColor White
Write-Host ""

Write-Host "Terminal 5 - Frontend (Puerto 5174):" -ForegroundColor Yellow
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host ""

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   URLs de Acceso" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend:  http://localhost:5174" -ForegroundColor Green
Write-Host "API REST:  http://localhost:8000" -ForegroundColor Green
Write-Host "WebSocket: ws://localhost:8001" -ForegroundColor Green
Write-Host "Admin:     http://localhost:8000/admin" -ForegroundColor Green
Write-Host ""

# 5. Verificar procesos corriendo
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Estado Actual de Procesos" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

$processes = Get-Process | Where-Object {
    $_.ProcessName -like "*python*" -or 
    $_.ProcessName -like "*redis*" -or 
    $_.ProcessName -like "*node*"
}

if ($processes) {
    Write-Host "Procesos relacionados encontrados:" -ForegroundColor Green
    $processes | Select-Object ProcessName, Id | Format-Table -AutoSize
} else {
    Write-Host "⚠️  No se encontraron procesos relacionados corriendo" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Script completado. Revisa los servicios faltantes arriba." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
