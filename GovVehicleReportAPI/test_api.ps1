# Script de prueba para llamar al endpoint /api/vehicle con placa de ejemplo
# Uso: .\test_api.ps1 -placa ABC123
param(
    [string]$placa = "ABC123"
)

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

Load-EnvFile -Path ".env"
$port = $env:PORT
if (-not $port) { $port = "7000" }

$baseUrl = "http://localhost:$port"

$uri = "$baseUrl/api/vehicle?placa=$placa"
Write-Host "Consultando $uri"
try {
    $resp = Invoke-RestMethod -Method Get -Uri $uri
    Write-Host "Respuesta:`n" ($resp | ConvertTo-Json -Depth 5)
} catch {
    Write-Host "Error al llamar API: $_"
}
