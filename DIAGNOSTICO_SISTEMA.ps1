# 🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🔍 DIAGNÓSTICO SISTEMA SIMPTV - Triple OCR" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# 1. REDIS
Write-Host "📊 1. REDIS SERVER" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
$redis = Get-Process redis-server -ErrorAction SilentlyContinue
if ($redis) {
    Write-Host "  ✅ Redis corriendo" -ForegroundColor Green
    Write-Host "     PID: $($redis.Id)" -ForegroundColor White
    Write-Host "     CPU: $($redis.CPU)" -ForegroundColor White
} else {
    Write-Host "  ❌ Redis NO está corriendo" -ForegroundColor Red
    Write-Host "     Solución: Start-Process -FilePath 'S:\Construccion\SIMPTV\backend\redis\redis-server.exe' -WindowStyle Minimized" -ForegroundColor Yellow
}

# 2. PYTHON PROCESSES (Django + Celery)
Write-Host "`n📊 2. PROCESOS PYTHON (Django + Celery)" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "  ✅ Python corriendo ($($pythonProcesses.Count) procesos)" -ForegroundColor Green
    foreach ($proc in $pythonProcesses) {
        Write-Host "     PID: $($proc.Id) | CPU: $($proc.CPU)" -ForegroundColor White
    }
} else {
    Write-Host "  ❌ Python NO está corriendo" -ForegroundColor Red
    Write-Host "     Necesitas iniciar Django y Celery" -ForegroundColor Yellow
}

# 3. PUERTOS
Write-Host "`n📊 3. PUERTOS EN USO" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray

# Puerto 8001 (Django)
$port8001 = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
if ($port8001) {
    Write-Host "  ✅ Puerto 8001 (Django) - ACTIVO" -ForegroundColor Green
    Write-Host "     Estado: $($port8001.State)" -ForegroundColor White
    Write-Host "     Dirección: $($port8001.LocalAddress):$($port8001.LocalPort)" -ForegroundColor White
} else {
    Write-Host "  ❌ Puerto 8001 (Django) - NO ACTIVO" -ForegroundColor Red
    Write-Host "     Solución: cd S:\Construccion\SIMPTV\backend; python manage.py runserver 8001" -ForegroundColor Yellow
}

# Puerto 5173 (Vite/Frontend)
$port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
if ($port5173) {
    Write-Host "  ✅ Puerto 5173 (Frontend Vite) - ACTIVO" -ForegroundColor Green
    Write-Host "     Estado: $($port5173.State)" -ForegroundColor White
} else {
    Write-Host "  ⚠️  Puerto 5173 (Frontend) - NO ACTIVO" -ForegroundColor Yellow
    Write-Host "     Verifica: cd S:\Construccion\SIMPTV\frontend; npm run dev" -ForegroundColor Yellow
}

# Puerto 3000 (Frontend alternativo)
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($port3000) {
    Write-Host "  ✅ Puerto 3000 (Frontend Alt) - ACTIVO" -ForegroundColor Green
    Write-Host "     Estado: $($port3000.State)" -ForegroundColor White
} else {
    Write-Host "  ℹ️  Puerto 3000 (Frontend Alt) - No en uso" -ForegroundColor Gray
}

# 4. NODE.JS PROCESSES (Frontend)
Write-Host "`n📊 4. PROCESOS NODE.JS (Frontend)" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
$nodeProcesses = Get-Process node -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "  ✅ Node.js corriendo ($($nodeProcesses.Count) procesos)" -ForegroundColor Green
    foreach ($proc in $nodeProcesses) {
        Write-Host "     PID: $($proc.Id)" -ForegroundColor White
    }
} else {
    Write-Host "  ❌ Node.js NO está corriendo" -ForegroundColor Red
    Write-Host "     Frontend no está activo" -ForegroundColor Yellow
}

# 5. GPU
Write-Host "`n📊 5. GPU (CUDA)" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
try {
    $gpuCheck = python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')" 2>$null
    if ($gpuCheck) {
        Write-Host "  ✅ GPU Detectada" -ForegroundColor Green
        Write-Host "     $gpuCheck" -ForegroundColor White
    } else {
        Write-Host "  ⚠️  GPU no detectada o PyTorch no instalado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ Error al verificar GPU" -ForegroundColor Red
}

# 6. VERIFICAR CONEXIÓN BACKEND
Write-Host "`n📊 6. VERIFICAR API BACKEND" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/api/traffic/cameras/" -TimeoutSec 3 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✅ API Backend responde correctamente" -ForegroundColor Green
        Write-Host "     Status: $($response.StatusCode)" -ForegroundColor White
        Write-Host "     URL: http://localhost:8001/api/traffic/cameras/" -ForegroundColor White
    }
} catch {
    Write-Host "  ❌ API Backend NO responde" -ForegroundColor Red
    Write-Host "     URL: http://localhost:8001/api/traffic/cameras/" -ForegroundColor White
    Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 7. VERIFICAR CONEXIÓN FRONTEND
Write-Host "`n📊 7. VERIFICAR FRONTEND" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 3 -ErrorAction SilentlyContinue
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "  ✅ Frontend responde correctamente" -ForegroundColor Green
        Write-Host "     Status: $($frontendResponse.StatusCode)" -ForegroundColor White
        Write-Host "     URL: http://localhost:5173" -ForegroundColor White
    }
} catch {
    Write-Host "  ❌ Frontend NO responde en puerto 5173" -ForegroundColor Red
    
    # Intentar puerto 3000
    try {
        $frontend3000 = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($frontend3000.StatusCode -eq 200) {
            Write-Host "  ✅ Frontend responde en puerto 3000" -ForegroundColor Green
            Write-Host "     URL: http://localhost:3000" -ForegroundColor White
        }
    } catch {
        Write-Host "  ❌ Frontend NO responde en puerto 3000" -ForegroundColor Red
        Write-Host "     Solución: cd S:\Construccion\SIMPTV\frontend; npm run dev" -ForegroundColor Yellow
    }
}

# RESUMEN
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "📋 RESUMEN DEL SISTEMA" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

$allGood = $true

if (-not $redis) {
    Write-Host "  ❌ Redis: NO" -ForegroundColor Red
    $allGood = $false
} else {
    Write-Host "  ✅ Redis: SÍ" -ForegroundColor Green
}

if (-not $pythonProcesses) {
    Write-Host "  ❌ Django/Celery: NO" -ForegroundColor Red
    $allGood = $false
} else {
    Write-Host "  ✅ Django/Celery: SÍ ($($pythonProcesses.Count) procesos)" -ForegroundColor Green
}

if (-not $port8001) {
    Write-Host "  ❌ Backend API (8001): NO" -ForegroundColor Red
    $allGood = $false
} else {
    Write-Host "  ✅ Backend API (8001): SÍ" -ForegroundColor Green
}

if (-not $nodeProcesses) {
    Write-Host "  ❌ Frontend (Node): NO" -ForegroundColor Red
    $allGood = $false
} else {
    Write-Host "  ✅ Frontend (Node): SÍ ($($nodeProcesses.Count) procesos)" -ForegroundColor Green
}

if ($port5173 -or $port3000) {
    Write-Host "  ✅ Frontend Accesible: SÍ" -ForegroundColor Green
} else {
    Write-Host "  ❌ Frontend Accesible: NO" -ForegroundColor Red
    $allGood = $false
}

Write-Host "`n" -NoNewline

if ($allGood) {
    Write-Host "🎉 SISTEMA COMPLETO FUNCIONAL" -ForegroundColor Green
    Write-Host "`nAccede a:" -ForegroundColor White
    if ($port5173) {
        Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Cyan
    } elseif ($port3000) {
        Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
    }
    Write-Host "  Backend:  http://localhost:8001/api/traffic/cameras/" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  SISTEMA INCOMPLETO - Revisa los servicios faltantes arriba" -ForegroundColor Yellow
    Write-Host "`n📝 COMANDOS PARA INICIAR:" -ForegroundColor White
    Write-Host "`n  # Terminal 1: Redis" -ForegroundColor Gray
    Write-Host "  Start-Process -FilePath 'S:\Construccion\SIMPTV\backend\redis\redis-server.exe' -WindowStyle Minimized" -ForegroundColor Cyan
    Write-Host "`n  # Terminal 2: Celery" -ForegroundColor Gray
    Write-Host "  cd S:\Construccion\SIMPTV\backend" -ForegroundColor Cyan
    Write-Host "  celery -A config worker --loglevel=info --pool=solo" -ForegroundColor Cyan
    Write-Host "`n  # Terminal 3: Django" -ForegroundColor Gray
    Write-Host "  cd S:\Construccion\SIMPTV\backend" -ForegroundColor Cyan
    Write-Host "  python manage.py runserver 8001" -ForegroundColor Cyan
    Write-Host "`n  # Terminal 4: Frontend" -ForegroundColor Gray
    Write-Host "  cd S:\Construccion\SIMPTV\frontend" -ForegroundColor Cyan
    Write-Host "  npm run dev" -ForegroundColor Cyan
}

Write-Host "`n============================================================`n" -ForegroundColor Cyan
