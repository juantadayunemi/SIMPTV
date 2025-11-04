# Script para reiniciar todos los servicios de TrafiSmart
# Ejecutar con: .\restart_services.ps1

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 79 -ForegroundColor Cyan
Write-Host "🔄 REINICIANDO SERVICIOS DE TRAFISMART" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 79 -ForegroundColor Cyan
Write-Host ""

# 1. Verificar directorio
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: Ejecuta este script desde la raíz del proyecto (D:\TrafiSmart)" -ForegroundColor Red
    exit 1
}

Write-Host "📋 1. VERIFICANDO CONFIGURACIÓN..." -ForegroundColor Yellow
Write-Host ""

# Activar entorno virtual y verificar configuración
Push-Location backend
& .\venv\Scripts\Activate.ps1

Write-Host "   Ejecutando verificación de detección de placas..." -ForegroundColor Gray
python check_plate_detection.py

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 79 -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 INSTRUCCIONES PARA REINICIAR SERVICIOS" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 79 -ForegroundColor Cyan
Write-Host ""

Write-Host "⚠️  IMPORTANTE: Este script solo verifica la configuración." -ForegroundColor Yellow
Write-Host "    Debes reiniciar manualmente los servicios en cada terminal:" -ForegroundColor Yellow
Write-Host ""

Write-Host "📝 SERVICIOS QUE DEBES REINICIAR:" -ForegroundColor White
Write-Host ""

Write-Host "1️⃣  CELERY WORKER (Terminal 'celery'):" -ForegroundColor Cyan
Write-Host "   - Presiona Ctrl+C para detener" -ForegroundColor Gray
Write-Host "   - Ejecuta: celery -A config worker -l INFO" -ForegroundColor Green
Write-Host ""

Write-Host "2️⃣  CELERY BEAT (Terminal 'celery' - otra ventana):" -ForegroundColor Cyan
Write-Host "   - Presiona Ctrl+C para detener" -ForegroundColor Gray
Write-Host "   - Ejecuta: celery -A config beat -l INFO" -ForegroundColor Green
Write-Host ""

Write-Host "3️⃣  DAPHNE (Terminal 'daphne') - Opcional:" -ForegroundColor Cyan
Write-Host "   - Presiona Ctrl+C para detener" -ForegroundColor Gray
Write-Host "   - Ejecuta: daphne -b 0.0.0.0 -p 8000 config.asgi:application" -ForegroundColor Green
Write-Host ""

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 79 -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ DESPUÉS DE REINICIAR:" -ForegroundColor Green
Write-Host "   1. Sube un video desde el frontend" -ForegroundColor White
Write-Host "   2. Espera a que se complete el análisis" -ForegroundColor White
Write-Host "   3. Verifica las carpetas:" -ForegroundColor White
Write-Host "      - backend/media/ROI YOLO/" -ForegroundColor Gray
Write-Host "      - backend/media/Placas/" -ForegroundColor Gray
Write-Host "      - backend/media/datos/" -ForegroundColor Gray
Write-Host ""

Write-Host "📖 Ver documentación completa en: PLATE_DETECTION_STATUS.md" -ForegroundColor Cyan
Write-Host ""

Pop-Location
