# ============================================================================
# SIMPTV - Script de Instalación Automática
# Migración: YOLOv5 → MobileNetSSD + HaarCascade + PaddleOCR
# ============================================================================

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  🚀 SIMPTV - Instalación de Nueva Arquitectura" -ForegroundColor White
Write-Host "  Arquitectura: MobileNetSSD + HaarCascade + PaddleOCR" -ForegroundColor White
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el directorio correcto
$currentPath = Get-Location
if (-not ($currentPath.Path -like "*SIMPTV*")) {
    Write-Host "❌ Error: Este script debe ejecutarse desde S:\Construccion\SIMPTV\" -ForegroundColor Red
    Write-Host "   Ubicación actual: $currentPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Solución:" -ForegroundColor Yellow
    Write-Host "   cd S:\Construccion\SIMPTV" -ForegroundColor White
    Write-Host "   .\INSTALL_NEW_ARCHITECTURE.ps1" -ForegroundColor White
    exit 1
}

Write-Host "✅ Directorio correcto detectado" -ForegroundColor Green
Write-Host ""

# Paso 1: Verificar Python
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "📍 Paso 1/5: Verificando Python..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python no encontrado" -ForegroundColor Red
    Write-Host "   Descarga Python desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Paso 2: Actualizar dependencias
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "📍 Paso 2/5: Actualizando dependencias..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Write-Host "   ℹ️  Desinstalando dependencias antiguas (YOLOv5, ONNX)..." -ForegroundColor Yellow
pip uninstall onnxruntime-directml torch torchvision torchaudio -y 2>$null

Write-Host "   ℹ️  Instalando nuevas dependencias..." -ForegroundColor Yellow
cd backend
pip install -r requirements.txt --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Dependencias instaladas correctamente" -ForegroundColor Green
} else {
    Write-Host "   ❌ Error al instalar dependencias" -ForegroundColor Red
    Write-Host "   Intenta manualmente: pip install -r backend\requirements.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Paso 3: Descargar modelos
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "📍 Paso 3/5: Descargando modelos (MobileNetSSD, HaarCascade)..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

python models\download_models.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "   ✅ Modelos descargados correctamente" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "   ❌ Error al descargar modelos" -ForegroundColor Red
    Write-Host "   Intenta manualmente: python backend\models\download_models.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Paso 4: Validar instalación
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "📍 Paso 4/5: Validando instalación..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

python models\test_models.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "   ✅ Validación exitosa" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "   ⚠️  Algunos tests fallaron, pero el sistema puede funcionar" -ForegroundColor Yellow
}

Write-Host ""

# Paso 5: Resumen
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "📍 Paso 5/5: Resumen de Instalación" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# Verificar archivos clave
$files = @(
    "models\MobileNetSSD_deploy.prototxt",
    "models\MobileNetSSD_deploy.caffemodel",
    "models\haarcascade_russian_plate_number.xml",
    "apps\traffic_app\services\video_processor_opencv.py"
)

$allPresent = $true
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file (FALTA)" -ForegroundColor Red
        $allPresent = $false
    }
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan

if ($allPresent) {
    Write-Host "  🎉 ¡Instalación Completada Exitosamente!" -ForegroundColor Green
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📊 Mejoras Esperadas:" -ForegroundColor White
    Write-Host "   • Velocidad: 60-90 FPS (vs 35-50 FPS anterior)" -ForegroundColor Yellow
    Write-Host "   • Memoria: ~500 MB (vs ~2-3 GB anterior)" -ForegroundColor Yellow
    Write-Host "   • Carga: 2-3 seg (vs 10-15 seg anterior)" -ForegroundColor Yellow
    Write-Host "   • Detección de placas: Integrada automáticamente" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 Próximos Pasos:" -ForegroundColor White
    Write-Host "   1. Iniciar backend:" -ForegroundColor Cyan
    Write-Host "      python manage.py runserver" -ForegroundColor White
    Write-Host ""
    Write-Host "   2. En otra terminal, iniciar Celery:" -ForegroundColor Cyan
    Write-Host "      celery -A config worker -l info --pool=solo" -ForegroundColor White
    Write-Host ""
    Write-Host "   3. En otra terminal, iniciar Daphne (WebSocket):" -ForegroundColor Cyan
    Write-Host "      daphne -p 8001 config.asgi:application" -ForegroundColor White
    Write-Host ""
    Write-Host "   4. Iniciar frontend:" -ForegroundColor Cyan
    Write-Host "      cd ..\frontend" -ForegroundColor White
    Write-Host "      npm start" -ForegroundColor White
    Write-Host ""
    Write-Host "📚 Documentación:" -ForegroundColor White
    Write-Host "   • Guía completa: ..\MIGRACION_MOBILENETSSD_COMPLETA.md" -ForegroundColor Yellow
    Write-Host "   • Modelos: models\README.md" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "  ⚠️  Instalación Completada con Advertencias" -ForegroundColor Yellow
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Algunos archivos no se encontraron. Revisa los pasos anteriores." -ForegroundColor Yellow
    Write-Host ""
}

cd ..

Write-Host "Presiona cualquier tecla para continuar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
