# 🚀 Script para Iniciar Sistema Completo

Write-Host "🎬 Iniciando Sistema de Análisis de Tráfico en Tiempo Real" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: Ejecuta este script desde la raíz del proyecto SIMPTV" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📋 INSTRUCCIONES:" -ForegroundColor Yellow
Write-Host "   Este script te ayudará a iniciar todos los servicios necesarios" -ForegroundColor Gray
Write-Host "   Necesitarás abrir 4 TERMINALES DIFERENTES (PowerShell)" -ForegroundColor Gray
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TERMINAL 1 - Redis Server" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Copia y ejecuta este comando en una nueva terminal PowerShell:" -ForegroundColor Yellow
Write-Host ""
Write-Host "cd s:\Construccion\SIMPTV\backend\redis" -ForegroundColor White
Write-Host ".\redis-server.exe redis.windows.conf" -ForegroundColor White
Write-Host ""
Write-Host "✅ Deberías ver: 'Ready to accept connections'" -ForegroundColor Green
Write-Host "⚠️  IMPORTANTE: Mantén esta terminal abierta (NO cerrar)" -ForegroundColor Yellow
Write-Host ""
Read-Host "Presiona ENTER cuando Redis esté corriendo"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TERMINAL 2 - Celery Worker (PROCESAMIENTO DE VIDEO)" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Copia y ejecuta este comando en una nueva terminal PowerShell:" -ForegroundColor Yellow
Write-Host ""
Write-Host "cd s:\Construccion\SIMPTV\backend" -ForegroundColor White
Write-Host "celery -A config worker -l info --pool=solo" -ForegroundColor White
Write-Host ""
Write-Host "✅ Deberías ver: 'celery@NOMBREPC ready'" -ForegroundColor Green
Write-Host "✅ Y la lista de tasks incluyendo: 'process_video_analysis'" -ForegroundColor Green
Write-Host "⚠️  IMPORTANTE: Mantén esta terminal abierta (NO cerrar)" -ForegroundColor Yellow
Write-Host "⚠️  ESTA ES LA TERMINAL MÁS IMPORTANTE - Sin Celery no hay procesamiento" -ForegroundColor Red
Write-Host ""
Read-Host "Presiona ENTER cuando Celery esté corriendo"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TERMINAL 3 - Django Backend" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Copia y ejecuta este comando en una nueva terminal PowerShell:" -ForegroundColor Yellow
Write-Host ""
Write-Host "cd s:\Construccion\SIMPTV\backend" -ForegroundColor White
Write-Host "python manage.py runserver 8001" -ForegroundColor White
Write-Host ""
Write-Host "✅ Deberías ver: 'Starting development server at http://127.0.0.1:8001/'" -ForegroundColor Green
Write-Host "⚠️  IMPORTANTE: Mantén esta terminal abierta (NO cerrar)" -ForegroundColor Yellow
Write-Host ""
Read-Host "Presiona ENTER cuando Django esté corriendo"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "TERMINAL 4 - Frontend React" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Copia y ejecuta este comando en una nueva terminal PowerShell:" -ForegroundColor Yellow
Write-Host ""
Write-Host "cd s:\Construccion\SIMPTV\frontend" -ForegroundColor White
Write-Host "npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "✅ Deberías ver: 'Local: http://localhost:5174/'" -ForegroundColor Green
Write-Host "⚠️  IMPORTANTE: Mantén esta terminal abierta (NO cerrar)" -ForegroundColor Yellow
Write-Host ""
Read-Host "Presiona ENTER cuando el Frontend esté corriendo"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ SISTEMA LISTO" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Abre tu navegador en: http://localhost:5174/camera/2" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎬 PASOS PARA VER EL VIDEO EN TIEMPO REAL:" -ForegroundColor Cyan
Write-Host "   1. Verifica que el video esté cargado (debería verse el video estático)" -ForegroundColor Gray
Write-Host "   2. Haz clic en el botón '▶️ Iniciar'" -ForegroundColor Gray
Write-Host "   3. Observa:" -ForegroundColor Gray
Write-Host "      - Badge rojo 'PROCESANDO EN TIEMPO REAL' aparece" -ForegroundColor Gray
Write-Host "      - Canvas muestra frames con cajas de colores" -ForegroundColor Gray
Write-Host "      - Panel verde muestra detecciones: 'HH:MM:SS tipo: car, placa ABC-1234'" -ForegroundColor Gray
Write-Host ""
Write-Host "🔍 VERIFICACIÓN EN TERMINAL 2 (Celery):" -ForegroundColor Yellow
Write-Host "   Cuando hagas clic en Iniciar, en la terminal de Celery deberías ver:" -ForegroundColor Gray
Write-Host "   - '📹 Iniciando procesamiento de video'" -ForegroundColor Gray
Write-Host "   - '🚗 Vehicle detected: track_id=..., type=car'" -ForegroundColor Gray
Write-Host "   - '🔤 Placa detectada: ABC-1234'" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  SI NO VES FRAMES PROCESADOS:" -ForegroundColor Red
Write-Host "   1. Verifica que Celery (Terminal 2) esté corriendo" -ForegroundColor Gray
Write-Host "   2. Verifica que Redis (Terminal 1) esté corriendo" -ForegroundColor Gray
Write-Host "   3. Abre la consola del navegador (F12) y busca errores" -ForegroundColor Gray
Write-Host "   4. Verifica en la terminal de Celery si hay errores" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Para más información, lee: REAL_TIME_PROCESSING_IMPLEMENTATION.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "✨ ¡Todo listo para procesar videos con YOLOv8 + OCR en tiempo real! ✨" -ForegroundColor Green
Write-Host ""
