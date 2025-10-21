# Script para iniciar el servidor Django en puerto 8001
# Captura errores y mantiene la ventana abierta

Write-Host "=" * 80
Write-Host "Iniciando servidor Django en puerto 8001..." -ForegroundColor Cyan
Write-Host "=" * 80

Set-Location "S:\Construccion\SIMPTV\backend"

Write-Host "`n[INFO] Directorio actual: $(Get-Location)" -ForegroundColor Yellow
Write-Host "[INFO] Comprobando manage.py..." -ForegroundColor Yellow

if (Test-Path "manage.py") {
    Write-Host "[OK] manage.py encontrado`n" -ForegroundColor Green
    
    Write-Host "[INFO] Iniciando servidor..." -ForegroundColor Yellow
    python manage.py runserver 8001
    
    $exitCode = $LASTEXITCODE
    Write-Host "`n[INFO] Servidor detenido con codigo de salida: $exitCode" -ForegroundColor Yellow
    
    if ($exitCode -ne 0) {
        Write-Host "[ERROR] El servidor termino con errores" -ForegroundColor Red
    }
} else {
    Write-Host "[ERROR] manage.py NO encontrado" -ForegroundColor Red
}

Write-Host "`nPresiona cualquier tecla para cerrar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
