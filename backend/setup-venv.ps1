# Script para recrear el entorno virtual de TrafiSmart Backend
Write-Host "Recreando entorno virtual..." -ForegroundColor Cyan

# Eliminar venv viejo si existe
if (Test-Path "venv") {
    Write-Host "Eliminando venv antiguo..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

# Crear nuevo venv
Write-Host "Creando nuevo entorno virtual..." -ForegroundColor Green
python -m venv venv

# Actualizar pip
Write-Host "Actualizando pip..." -ForegroundColor Green
.\venv\Scripts\python.exe -m pip install --upgrade pip

# Instalar dependencias
Write-Host "Instalando dependencias..." -ForegroundColor Green
.\venv\Scripts\pip.exe install -r requirements.txt

Write-Host ""
Write-Host "Entorno virtual configurado correctamente!" -ForegroundColor Green
Write-Host ""
Write-Host "Para activarlo manualmente usa:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para iniciar el servidor:" -ForegroundColor Cyan
Write-Host "  python manage.py runserver_plus" -ForegroundColor Yellow
