# ============================================================================
# LIMPIEZA DE ESPACIO EN DISCO - Eliminar YOLOv8 y paquetes innecesarios
# ============================================================================

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "🧹 LIMPIEZA DE ESPACIO EN DISCO C" -ForegroundColor Yellow
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date

# ============================================================================
# 1. DESINSTALAR ULTRALYTICS (YOLOv8) - No se usa, tenemos YOLOv5 ONNX
# ============================================================================
Write-Host "📦 1. Desinstalando Ultralytics (YOLOv8)..." -ForegroundColor Green
Write-Host "   ℹ️  No lo usamos, tenemos YOLOv5m ONNX (más rápido)" -ForegroundColor Gray

try {
    $output = pip uninstall ultralytics -y 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Ultralytics desinstalado (~500MB liberados)" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  Ultralytics no estaba instalado" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ℹ️  Ultralytics no encontrado" -ForegroundColor Gray
}

# ============================================================================
# 2. LIMPIAR CACHE PIP (puede ocupar GB)
# ============================================================================
Write-Host ""
Write-Host "📦 2. Limpiando cache de pip..." -ForegroundColor Green

# Verificar tamaño cache antes
$pipCachePath = "$env:LOCALAPPDATA\pip\cache"
if (Test-Path $pipCachePath) {
    $cacheSizeBefore = (Get-ChildItem $pipCachePath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "   📊 Tamaño cache actual: $([math]::Round($cacheSizeBefore, 2)) MB" -ForegroundColor Gray
    
    pip cache purge 2>&1 | Out-Null
    
    if (Test-Path $pipCachePath) {
        $cacheSizeAfter = (Get-ChildItem $pipCachePath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
        $freed = $cacheSizeBefore - $cacheSizeAfter
        Write-Host "   ✅ Cache limpiado (~$([math]::Round($freed, 2)) MB liberados)" -ForegroundColor Green
    } else {
        Write-Host "   ✅ Cache completamente eliminado (~$([math]::Round($cacheSizeBefore, 2)) MB liberados)" -ForegroundColor Green
    }
} else {
    Write-Host "   ℹ️  No hay cache de pip" -ForegroundColor Gray
}

# ============================================================================
# 3. ELIMINAR MODELOS YOLOV8 DESCARGADOS (.pt de ultralytics)
# ============================================================================
Write-Host ""
Write-Host "📦 3. Buscando modelos YOLOv8 descargados..." -ForegroundColor Green

$yolov8Paths = @(
    "$env:USERPROFILE\.cache\torch\hub\ultralytics_yolov5_master",
    "$env:USERPROFILE\.cache\ultralytics",
    "$env:APPDATA\Ultralytics"
)

$totalFreed = 0
foreach ($path in $yolov8Paths) {
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
        Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   ✅ Eliminado: $path (~$([math]::Round($size, 2)) MB)" -ForegroundColor Green
        $totalFreed += $size
    }
}

if ($totalFreed -eq 0) {
    Write-Host "   ℹ️  No se encontraron modelos YOLOv8" -ForegroundColor Gray
} else {
    Write-Host "   ✅ Total liberado: ~$([math]::Round($totalFreed, 2)) MB" -ForegroundColor Green
}

# ============================================================================
# 4. LIMPIAR CACHE PADDLEOCR
# ============================================================================
Write-Host ""
Write-Host "📦 4. Limpiando cache de PaddleOCR..." -ForegroundColor Green

$paddleCachePaths = @(
    "$env:USERPROFILE\.paddleocr",
    "$env:APPDATA\paddleocr"
)

$paddleFreed = 0
foreach ($path in $paddleCachePaths) {
    if (Test-Path $path) {
        # No eliminar modelos, solo cache temporal
        $tempPath = Join-Path $path "temp"
        if (Test-Path $tempPath) {
            $size = (Get-ChildItem $tempPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
            Remove-Item $tempPath -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "   ✅ Cache temporal eliminado (~$([math]::Round($size, 2)) MB)" -ForegroundColor Green
            $paddleFreed += $size
        }
    }
}

if ($paddleFreed -eq 0) {
    Write-Host "   ℹ️  No hay cache temporal de PaddleOCR" -ForegroundColor Gray
}

# ============================================================================
# 5. LIMPIAR ARCHIVOS TEMPORALES PYTHON
# ============================================================================
Write-Host ""
Write-Host "📦 5. Limpiando archivos temporales Python..." -ForegroundColor Green

$pyTempPaths = @(
    "$env:TEMP\*.pyc",
    "$env:TEMP\pip-*",
    "$env:LOCALAPPDATA\Temp\*.pyc"
)

$tempFreed = 0
foreach ($pattern in $pyTempPaths) {
    $files = Get-ChildItem $pattern -ErrorAction SilentlyContinue
    if ($files) {
        $size = ($files | Measure-Object -Property Length -Sum).Sum / 1MB
        $files | Remove-Item -Force -ErrorAction SilentlyContinue
        $tempFreed += $size
    }
}

if ($tempFreed -gt 0) {
    Write-Host "   ✅ Archivos temporales eliminados (~$([math]::Round($tempFreed, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  No hay archivos temporales significativos" -ForegroundColor Gray
}

# ============================================================================
# 6. VERIFICAR PAQUETES PESADOS INNECESARIOS
# ============================================================================
Write-Host ""
Write-Host "📦 6. Verificando paquetes pesados..." -ForegroundColor Green

$heavyPackages = @{
    "jupyter" = "~500MB (¿Lo usas?)"
    "notebook" = "~300MB (¿Lo usas?)"
    "ipython" = "~100MB (¿Lo usas?)"
    "matplotlib" = "~200MB (¿Lo usas?)"
    "seaborn" = "~50MB (¿Lo usas?)"
    "pandas" = "~100MB (Solo si lo usas para análisis)"
}

Write-Host "   ℹ️  Paquetes instalados que podrías no necesitar:" -ForegroundColor Gray
foreach ($pkg in $heavyPackages.Keys) {
    $installed = pip show $pkg 2>&1 | Select-String "Name:"
    if ($installed) {
        Write-Host "      • $pkg $($heavyPackages[$pkg])" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "   💡 Para desinstalarlos manualmente:" -ForegroundColor Cyan
Write-Host "      pip uninstall jupyter notebook ipython matplotlib seaborn -y" -ForegroundColor Gray

# ============================================================================
# 7. RESUMEN
# ============================================================================
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "📊 RESUMEN DE LIMPIEZA" -ForegroundColor Yellow
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Operaciones completadas:" -ForegroundColor Green
Write-Host "   1. Ultralytics (YOLOv8) desinstalado" -ForegroundColor Gray
Write-Host "   2. Cache pip limpiado" -ForegroundColor Gray
Write-Host "   3. Modelos YOLOv8 eliminados" -ForegroundColor Gray
Write-Host "   4. Cache PaddleOCR limpiado" -ForegroundColor Gray
Write-Host "   5. Archivos temporales Python eliminados" -ForegroundColor Gray
Write-Host ""

# Espacio total liberado estimado
$totalSpaceFreed = $cacheSizeBefore + $totalFreed + $paddleFreed + $tempFreed
Write-Host "💾 Espacio estimado liberado: ~$([math]::Round($totalSpaceFreed, 2)) MB" -ForegroundColor Green
Write-Host "⏱️  Tiempo: $([math]::Round($duration, 1)) segundos" -ForegroundColor Gray
Write-Host ""

# ============================================================================
# 8. RECOMENDACIONES ADICIONALES
# ============================================================================
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "💡 RECOMENDACIONES ADICIONALES" -ForegroundColor Yellow
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para liberar MÁS espacio en C:\" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Limpiar Disco Windows:" -ForegroundColor Green
Write-Host "   cleanmgr /d C:" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Vaciar Papelera:" -ForegroundColor Green
Write-Host "   Clear-RecycleBin -Force" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Desinstalar paquetes Python NO usados:" -ForegroundColor Green
Write-Host "   pip list  # Ver todos instalados" -ForegroundColor Gray
Write-Host "   pip uninstall <paquete> -y" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Mover venv a disco S:\ (si tiene mucho espacio):" -ForegroundColor Green
Write-Host "   • Actual: S:\Construccion\SIMPTV\backend\venv\" -ForegroundColor Gray
Write-Host "   • Si está en C:\, moverlo a S:\" -ForegroundColor Gray
Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "✅ LIMPIEZA COMPLETADA" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Cyan
