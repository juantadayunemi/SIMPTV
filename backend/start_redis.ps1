# Script para descargar y ejecutar Redis en Windows
# Autor: TrafiSmart
# Fecha: 2025-10-10

Write-Host "🔧 Instalando Redis para Windows..." -ForegroundColor Cyan

# Crear directorio para Redis
$redisDir = "D:\TrafiSmart\backend\redis"
if (-not (Test-Path $redisDir)) {
    New-Item -ItemType Directory -Path $redisDir | Out-Null
}

# URL de descarga de Redis para Windows
$redisUrl = "https://github.com/microsoftarchive/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.zip"
$zipPath = "$redisDir\redis.zip"

# Descargar Redis si no existe
if (-not (Test-Path "$redisDir\redis-server.exe")) {
    Write-Host "📥 Descargando Redis..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $redisUrl -OutFile $zipPath
    
    Write-Host "📦 Extrayendo archivos..." -ForegroundColor Yellow
    Expand-Archive -Path $zipPath -DestinationPath $redisDir -Force
    Remove-Item $zipPath
    
    Write-Host "✅ Redis descargado correctamente" -ForegroundColor Green
} else {
    Write-Host "✅ Redis ya está instalado" -ForegroundColor Green
}

# Iniciar Redis
Write-Host "🚀 Iniciando Redis en el puerto 6379..." -ForegroundColor Cyan
Set-Location $redisDir
Start-Process -FilePath ".\redis-server.exe" -ArgumentList "redis.windows.conf" -WindowStyle Normal

Write-Host ""
Write-Host "✅ Redis está corriendo en localhost:6379" -ForegroundColor Green
Write-Host "📝 Para detenerlo, cierra la ventana de Redis" -ForegroundColor Yellow
Write-Host ""
