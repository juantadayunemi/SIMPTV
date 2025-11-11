# Script para probar los nuevos endpoints de permisos
# Asegúrate de que el servidor Django esté corriendo en http://localhost:8000

$baseUrl = "http://localhost:8000/api/auth"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "PRUEBAS DE API DE PERMISOS" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  ASEGÚRATE DE QUE EL SERVIDOR DJANGO ESTÉ CORRIENDO" -ForegroundColor Yellow
Write-Host ""

# Solicitar token
Write-Host "1. Ingresa tu token de acceso (Bearer token):" -ForegroundColor Yellow
$token = Read-Host

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# TEST 1: Obtener permisos del rol ADMIN
Write-Host "`n==================================" -ForegroundColor Green
Write-Host "TEST 1: GET /admin/roles/ADMIN/permissions/" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/admin/roles/ADMIN/permissions/" -Method GET -Headers $headers
    Write-Host "✅ ÉXITO:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5
} catch {
    Write-Host "❌ ERROR:" -ForegroundColor Red
    $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $reader.ReadToEnd()
    }
}

# TEST 2: Actualizar permisos del rol OPERATOR (agregar traffic:delete)
Write-Host "`n==================================" -ForegroundColor Green
Write-Host "TEST 2: POST /admin/roles/OPERATOR/permissions/" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

$customPerms = @{
    permissions = @(
        @{ permission = "traffic:delete"; isGranted = $true }
        @{ permission = "users:read"; isGranted = $true }
    )
} | ConvertTo-Json

Write-Host "Enviando:" -ForegroundColor Yellow
Write-Host $customPerms

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/admin/roles/OPERATOR/permissions/" -Method POST -Headers $headers -Body $customPerms
    Write-Host "✅ ÉXITO:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5
} catch {
    Write-Host "❌ ERROR:" -ForegroundColor Red
    $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $reader.ReadToEnd()
    }
}

# TEST 3: Obtener permisos efectivos de un usuario
Write-Host "`n==================================" -ForegroundColor Green
Write-Host "TEST 3: GET /admin/users/{userId}/permissions/" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

Write-Host "`nIngresa el ID del usuario a consultar:" -ForegroundColor Yellow
$userId = Read-Host

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/admin/users/$userId/permissions/" -Method GET -Headers $headers
    Write-Host "✅ ÉXITO:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5
} catch {
    Write-Host "❌ ERROR:" -ForegroundColor Red
    $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $reader.ReadToEnd()
    }
}

# TEST 4: Crear override de permiso para usuario
Write-Host "`n==================================" -ForegroundColor Green
Write-Host "TEST 4: POST /admin/users/{userId}/permissions/override/" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

$override = @{
    permission = "traffic:delete"
    isGranted = $true
    overrideReason = "Permiso temporal de prueba"
} | ConvertTo-Json

Write-Host "Enviando override para usuario $userId" -ForegroundColor Yellow
Write-Host $override

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/admin/users/$userId/permissions/override/" -Method POST -Headers $headers -Body $override
    Write-Host "✅ ÉXITO:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5
} catch {
    Write-Host "❌ ERROR:" -ForegroundColor Red
    $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $reader.ReadToEnd()
    }
}

Write-Host "`n==================================" -ForegroundColor Cyan
Write-Host "PRUEBAS COMPLETADAS" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
