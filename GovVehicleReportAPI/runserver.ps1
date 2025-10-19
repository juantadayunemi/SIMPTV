# Wrapper PowerShell script to run the Django dev server using PORT from .env
param()

function Load-EnvFile {
    param([string]$Path = ".env")
    if (-Not (Test-Path $Path)) { return }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) { return }
        $parts = $line -split "=", 2
        $k = $parts[0].Trim()
        $v = $parts[1].Trim().Trim('"').Trim("'")
        if (-not [string]::IsNullOrEmpty($k) -and -not (Get-ChildItem env:$k -ErrorAction SilentlyContinue)) {
            Set-Item env:$k $v
        }
    }
}

Write-Host "Cargando .env (si existe) y activando venv si está presente..."
Load-EnvFile -Path ".env"

if (Test-Path .\.venv\Scripts\Activate.ps1) {
    Write-Host "Activando entorno virtual .venv"
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "No se encontró .venv; se usará el python del sistema"
}

$port = $env:PORT
if (-not $port) { $port = "7000" }

Write-Host "Iniciando servidor en http://localhost:$port"
python manage.py runserver $port
