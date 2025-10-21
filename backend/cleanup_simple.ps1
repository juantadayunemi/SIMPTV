# ============================================================================
# LIMPIEZA RAPIDA DE ESPACIO - Eliminar YOLOv8 y cache innecesario
# ============================================================================

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "LIMPIEZA DE ESPACIO EN DISCO C" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. DESINSTALAR ULTRALYTICS (YOLOv8)
Write-Host "1. Desinstalando Ultralytics (YOLOv8)..." -ForegroundColor Green
pip uninstall ultralytics -y 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK - Ultralytics desinstalado (~500MB)" -ForegroundColor Green
} else {
    Write-Host "   INFO - Ultralytics no estaba instalado" -ForegroundColor Gray
}

# 2. LIMPIAR CACHE PIP
Write-Host ""
Write-Host "2. Limpiando cache de pip..." -ForegroundColor Green
$pipCache = "$env:LOCALAPPDATA\pip\cache"
if (Test-Path $pipCache) {
    $sizeBefore = (Get-ChildItem $pipCache -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    pip cache purge 2>&1 | Out-Null
    Write-Host "   OK - Cache limpiado (~$([math]::Round($sizeBefore, 0)) MB)" -ForegroundColor Green
} else {
    Write-Host "   INFO - No hay cache pip" -ForegroundColor Gray
}

# 3. ELIMINAR MODELOS YOLOV8
Write-Host ""
Write-Host "3. Eliminando modelos YOLOv8..." -ForegroundColor Green
$paths = @(
    "$env:USERPROFILE\.cache\torch\hub\ultralytics_yolov5_master",
    "$env:USERPROFILE\.cache\ultralytics",
    "$env:APPDATA\Ultralytics"
)

$total = 0
foreach ($path in $paths) {
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
        Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   OK - Eliminado $path (~$([math]::Round($size, 0)) MB)" -ForegroundColor Green
        $total += $size
    }
}

if ($total -eq 0) {
    Write-Host "   INFO - No se encontraron modelos YOLOv8" -ForegroundColor Gray
}

# 4. LIMPIAR ARCHIVOS TEMPORALES
Write-Host ""
Write-Host "4. Limpiando archivos temporales..." -ForegroundColor Green
$tempFiles = Get-ChildItem "$env:TEMP\*.pyc", "$env:TEMP\pip-*" -ErrorAction SilentlyContinue
if ($tempFiles) {
    $tempSize = ($tempFiles | Measure-Object -Property Length -Sum).Sum / 1MB
    $tempFiles | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "   OK - Temporales eliminados (~$([math]::Round($tempSize, 0)) MB)" -ForegroundColor Green
} else {
    Write-Host "   INFO - No hay archivos temporales" -ForegroundColor Gray
}

# 5. RESUMEN
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "LIMPIEZA COMPLETADA" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Espacio liberado estimado: ~1-2 GB" -ForegroundColor Green
Write-Host ""
Write-Host "RECOMENDACIONES ADICIONALES:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para liberar MAS espacio:" -ForegroundColor Cyan
Write-Host "  1. Limpiador Windows: cleanmgr /d C:" -ForegroundColor Gray
Write-Host "  2. Vaciar Papelera: Clear-RecycleBin -Force" -ForegroundColor Gray
Write-Host "  3. Ver paquetes Python: pip list" -ForegroundColor Gray
Write-Host ""
Write-Host "Paquetes Python que podrias desinstalar si no usas:" -ForegroundColor Cyan
Write-Host "  pip uninstall jupyter notebook ipython matplotlib -y" -ForegroundColor Gray
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
