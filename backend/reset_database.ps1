# Script para limpiar base de datos y migrations
# Ejecutar desde: d:\TrafiSmart\backend

Write-Host "🧹 Limpiando base de datos y migrations..." -ForegroundColor Cyan
Write-Host ""

# 1. Eliminar base de datos SQLite
if (Test-Path "db.sqlite3") {
    Remove-Item "db.sqlite3" -Force
    Write-Host "✅ Base de datos eliminada" -ForegroundColor Green
} else {
    Write-Host "⚠️  Base de datos no encontrada" -ForegroundColor Yellow
}

# 2. Eliminar migrations antiguas (excepto __init__.py)
Write-Host ""
Write-Host "🗑️  Eliminando migrations antiguas..." -ForegroundColor Cyan

$migrationsDeleted = 0

Get-ChildItem -Path "apps" -Filter "migrations" -Recurse -Directory | ForEach-Object {
    $migrationsDir = $_.FullName
    $appName = Split-Path (Split-Path $migrationsDir -Parent) -Leaf
    
    Get-ChildItem -Path $migrationsDir -Filter "*.py" -File | Where-Object {
        $_.Name -ne "__init__.py"
    } | ForEach-Object {
        Remove-Item $_.FullName -Force
        $migrationsDeleted++
        Write-Host "   ❌ $appName/$($_.Name)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ $migrationsDeleted migrations eliminadas" -ForegroundColor Green

# 3. Crear nuevas migrations
Write-Host ""
Write-Host "📝 Creando nuevas migrations con camelCase..." -ForegroundColor Cyan
python manage.py makemigrations

# 4. Aplicar migrations
Write-Host ""
Write-Host "🚀 Aplicando migrations..." -ForegroundColor Cyan
python manage.py migrate

Write-Host ""
Write-Host "✨ ¡Listo! Base de datos limpia con camelCase" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos pasos:" -ForegroundColor Yellow
Write-Host "   1. python manage.py createsuperuser (si necesitas)" -ForegroundColor White
Write-Host "   2. python manage.py runserver" -ForegroundColor White
Write-Host ""
