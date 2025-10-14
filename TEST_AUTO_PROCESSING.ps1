# 🔧 Script para Probar Procesamiento Automático

Write-Host "🎬 Probando sistema de procesamiento automático" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# 1. Verificar que estamos en el directorio correcto
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: Ejecuta este script desde la raíz del proyecto" -ForegroundColor Red
    exit 1
}

Write-Host "📋 PASO 1: Resetear análisis a PENDING" -ForegroundColor Yellow
Write-Host "Ejecutando comando..." -ForegroundColor Gray

$resetCommand = @"
from apps.traffic_app.models import TrafficAnalysis
try:
    a = TrafficAnalysis.objects.get(id=4)
    a.status = 'PENDING'
    a.isPlaying = False
    a.isPaused = False
    a.save()
    print(f'✅ Análisis {a.id} reseteado: status={a.status}, isPlaying={a.isPlaying}')
except Exception as e:
    print(f'❌ Error: {e}')
"@

cd backend
python manage.py shell -c $resetCommand
cd ..

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "📋 PASO 2: Instrucciones para probar" -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣ Asegúrate de que Django esté corriendo en puerto 8001" -ForegroundColor White
Write-Host "   Si no está corriendo, ejecuta:" -ForegroundColor Gray
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   python manage.py runserver 8001" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣ Asegúrate de que el frontend esté corriendo" -ForegroundColor White
Write-Host "   Si no está corriendo, ejecuta en otra terminal:" -ForegroundColor Gray
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "3️⃣ Abre el navegador:" -ForegroundColor White
Write-Host "   http://localhost:5174/camera/2" -ForegroundColor White
Write-Host ""
Write-Host "4️⃣ Abre la consola del navegador (F12)" -ForegroundColor White
Write-Host ""
Write-Host "5️⃣ Haz clic en el botón verde '▶️ Iniciar'" -ForegroundColor White
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🔍 QUÉ ESPERAR" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "En la TERMINAL DE DJANGO deberías ver:" -ForegroundColor Yellow
Write-Host "  🚀 Lanzando procesamiento para análisis 4" -ForegroundColor Gray
Write-Host "  ✅ Thread de procesamiento iniciado" -ForegroundColor Gray
Write-Host "  🔄 run_processing() iniciado para análisis 4" -ForegroundColor Gray
Write-Host "  🚀 Intentando Celery..." -ForegroundColor Gray
Write-Host "  ⚠️ Celery no disponible: ..." -ForegroundColor Gray
Write-Host "  🎬 Ejecutando runner standalone para análisis 4..." -ForegroundColor Gray
Write-Host "  ✅ Módulo runner importado correctamente" -ForegroundColor Gray
Write-Host "  🎬 STANDALONE: Iniciando análisis 4" -ForegroundColor Gray
Write-Host "  📹 Iniciando análisis: traffic_videos/..." -ForegroundColor Gray
Write-Host "  ✅ Video encontrado: XX.XXMB" -ForegroundColor Gray
Write-Host "  🚀 VideoProcessor usando device: cuda/cpu" -ForegroundColor Gray
Write-Host "  🔤 Inicializando EasyOCR..." -ForegroundColor Gray
Write-Host "  ✅ YOLOv8 + OCR cargados" -ForegroundColor Gray
Write-Host "  📊 Video info: 1920x1080, 30 FPS, 9000 frames" -ForegroundColor Gray
Write-Host "  🎬 Iniciando procesamiento de video..." -ForegroundColor Gray
Write-Host "  🚗 Vehículo detectado: ckxxxxxx (car)" -ForegroundColor Gray
Write-Host "  🔤 Placa detectada: ABC-1234" -ForegroundColor Gray
Write-Host ""
Write-Host "En la CONSOLA DEL NAVEGADOR (F12) deberías ver:" -ForegroundColor Yellow
Write-Host "  ✅ Análisis iniciado: {analysis_id: 4, ...}" -ForegroundColor Gray
Write-Host "  ▶️ Mostrando frames procesados con YOLOv8 + OCR" -ForegroundColor Gray
Write-Host "  ✅ WebSocket conectado para análisis: 4" -ForegroundColor Gray
Write-Host "  📸 Frame recibido: 30 detecciones: 5" -ForegroundColor Gray
Write-Host "  ✅ Frame dibujado en canvas: 1920 x 1080" -ForegroundColor Gray
Write-Host "  🚗 Vehículo detectado (raw): {...}" -ForegroundColor Gray
Write-Host ""
Write-Host "En la PÁGINA WEB deberías ver:" -ForegroundColor Yellow
Write-Host "  ✅ Badge rojo 'PROCESANDO EN TIEMPO REAL'" -ForegroundColor Gray
Write-Host "  ✅ Canvas con frames procesados (cajas de colores)" -ForegroundColor Gray
Write-Host "  ✅ Panel verde con detecciones: '14:25:18 tipo: car, placa ABC-1234'" -ForegroundColor Gray
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "⚠️ TROUBLESHOOTING" -ForegroundColor Red
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "Si NO VES los mensajes en Django:" -ForegroundColor Yellow
Write-Host "  → Reinicia el servidor Django (Ctrl+C y volver a iniciar)" -ForegroundColor Gray
Write-Host ""
Write-Host "Si Canvas está NEGRO:" -ForegroundColor Yellow
Write-Host "  → Verifica que Django muestre los mensajes de arriba" -ForegroundColor Gray
Write-Host "  → Verifica consola del navegador (F12) para ver errores" -ForegroundColor Gray
Write-Host ""
Write-Host "Si dice 'Esperando detecciones...' pero no cambia:" -ForegroundColor Yellow
Write-Host "  → Espera ~30 segundos (procesamiento toma tiempo)" -ForegroundColor Gray
Write-Host "  → Verifica que Django muestre '🚗 Vehículo detectado'" -ForegroundColor Gray
Write-Host ""
Write-Host "✨ ¡Listo para probar!" -ForegroundColor Green
Write-Host ""
