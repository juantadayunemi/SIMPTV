# Script para iniciar todos los servicios del sistema

Write-Host "🚀 Iniciando Sistema de Análisis de Tráfico" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# 1. Verificar Redis
Write-Host "1️⃣ Verificando Redis..." -ForegroundColor Cyan
$redisProcess = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
if ($redisProcess) {
    Write-Host "✅ Redis ya está corriendo (PID: $($redisProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "⚠️ Redis no está corriendo" -ForegroundColor Yellow
    Write-Host "Iniciando Redis..." -ForegroundColor Yellow
    Start-Process -FilePath "backend\redis\redis-server.exe" -ArgumentList "backend\redis\redis.windows.conf" -WindowStyle Minimized
    Start-Sleep -Seconds 2
    Write-Host "✅ Redis iniciado" -ForegroundColor Green
}

Write-Host ""

# 2. Verificar Django
Write-Host "2️⃣ Verificando Django..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/api/traffic/cameras/" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Django está corriendo en puerto 8001" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Django no está respondiendo en puerto 8001" -ForegroundColor Yellow
    Write-Host "Inicia Django manualmente:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor Gray
    Write-Host "  python manage.py runserver 0.0.0.0:8001" -ForegroundColor Gray
}

Write-Host ""

# 3. Verificar Celery
Write-Host "3️⃣ Verificando Celery..." -ForegroundColor Cyan
$celeryProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*celery*"}
if ($celeryProcess) {
    Write-Host "✅ Celery ya está corriendo" -ForegroundColor Green
} else {
    Write-Host "⚠️ Celery no está corriendo" -ForegroundColor Yellow
    Write-Host "⚠️ ¡IMPORTANTE! Debes iniciar Celery manualmente:" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Abre una nueva terminal PowerShell y ejecuta:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor Cyan
    Write-Host "  celery -A config worker -l info --pool=solo" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ""

# 4. Verificar Frontend
Write-Host "4️⃣ Verificando Frontend..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5174" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Frontend está corriendo en puerto 5174" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Frontend no está respondiendo en puerto 5174" -ForegroundColor Yellow
    Write-Host "Inicia Frontend manualmente:" -ForegroundColor Yellow
    Write-Host "  cd frontend" -ForegroundColor Gray
    Write-Host "  npm run dev" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "📊 Resumen de Servicios:" -ForegroundColor Green
Write-Host "  ✅ Redis:    http://localhost:6379" -ForegroundColor White
Write-Host "  ✅ Django:   http://localhost:8001" -ForegroundColor White
Write-Host "  ⚠️ Celery:   (Debe estar corriendo)" -ForegroundColor Yellow
Write-Host "  ✅ Frontend: http://localhost:5174" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Para usar el sistema:" -ForegroundColor Cyan
Write-Host "  1. Ir a: http://localhost:5174/camera/2" -ForegroundColor White
Write-Host "  2. Verificar que el video se muestra" -ForegroundColor White
Write-Host "  3. Click en botón 'Iniciar' (rojo)" -ForegroundColor White
Write-Host "  4. Ver detecciones en tiempo real" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentación:" -ForegroundColor Cyan
Write-Host "  - START_ANALYSIS_GUIDE.md" -ForegroundColor White
Write-Host "  - PORT_FIX_SOLUTION.md" -ForegroundColor White
Write-Host "  - DIAGNOSTIC_GUIDE.md" -ForegroundColor White
Write-Host ""
