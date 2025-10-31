# ===========================================
# Script: runAppDev.ps1
# Ejecuta Celery, Daphne y Runserver en VS Code
# ===========================================

# Obtener el directorio actual
$currentPath = Get-Location

# Verificar si estamos dentro de la carpeta "backend"
if ((Split-Path $currentPath -Leaf) -ne "backend") {
    Write-Host "❌ Ubíquese en la carpeta 'backend' antes de ejecutar este script." -ForegroundColor Red
    Write-Host "   Ejemplo: cd .\backend" -ForegroundColor Yellow
    exit
}

# Ruta del entorno virtual
$venvActivate = ".\venv\Scripts\Activate.ps1"

if (-Not (Test-Path $venvActivate)) {
    Write-Host "⚠️ No se encontró el entorno virtual en '$venvActivate'." -ForegroundColor Yellow
    Write-Host "   Cree uno con: python -m venv venv"
    exit
}

# ===========================================
# Función auxiliar para crear terminales
# ===========================================
function New-VSCTerminal($name, $command) {
    # Enviar comando al terminal integrado de VS Code
    $encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes("& '$venvActivate'; $command"))
    code --new-window --command "workbench.action.terminal.new" | Out-Null
    code --command "workbench.action.terminal.sendSequence" --args "{`"text`": `"powershell -EncodedCommand $encodedCommand`"}"
}

# ===========================================
# Ejecutar los servicios en terminales integradas
# ===========================================
Write-Host "🚀 Iniciando Celery..." -ForegroundColor Green
Start-Sleep -Milliseconds 300
code --command "workbench.action.terminal.new" --reuse-window
code --command "workbench.action.terminal.sendSequence" --args "{`"text`": `"& $venvActivate; celery -A config worker --loglevel=info --pool=solo`"}"

Write-Host "🌐 Iniciando Daphne..." -ForegroundColor Green
Start-Sleep -Milliseconds 300
code --command "workbench.action.terminal.new" --reuse-window
code --command "workbench.action.terminal.sendSequence" --args "{`"text`": `"& $venvActivate; daphne -b 0.0.0.0 -p 8001 config.asgi:application`"}"

Write-Host "🧩 Iniciando servidor Django..." -ForegroundColor Green
Start-Sleep -Milliseconds 300
code --command "workbench.action.terminal.new" --reuse-window
code --command "workbench.action.terminal.sendSequence" --args "{`"text`": `"& $venvActivate; python manage.py runserver`"}"

Write-Host ""
Write-Host "✅ Todos los servicios se iniciaron en terminales integradas de VS Code." -ForegroundColor Cyan
