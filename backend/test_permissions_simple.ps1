# Script simple para probar permisos
$baseUrl = "http://localhost:8000/api/auth"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PRUEBA DE SISTEMA DE PERMISOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Login para obtener token
Write-Host "PASO 1: LOGIN" -ForegroundColor Yellow
Write-Host "Ingresa tu email de admin:" -ForegroundColor White
$email = Read-Host
Write-Host "Ingresa tu password:" -ForegroundColor White
$password = Read-Host -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

$loginBody = @{
    email = $email
    password = $passwordPlain
} | ConvertTo-Json

Write-Host "`nIntentando login..." -ForegroundColor Yellow

try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/login/" -Method POST -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token  # Corregido: access_token en lugar de access
    
    Write-Host "✅ Login exitoso!" -ForegroundColor Green
    Write-Host "Usuario: $($loginResponse.user.email)" -ForegroundColor Gray
    Write-Host "Token obtenido: $($token.Substring(0, 20))..." -ForegroundColor Gray
    Write-Host ""
    
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    # Paso 2: Ver permisos del rol VIEWER
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "PASO 2: VER PERMISOS DEL ROL VIEWER" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    
    $response = Invoke-RestMethod -Uri "$baseUrl/admin/roles/VIEWER/permissions/" -Method GET -Headers $headers
    
    Write-Host "✅ Permisos obtenidos:" -ForegroundColor Green
    Write-Host "Rol: $($response.role)" -ForegroundColor White
    Write-Host "`nPermisos por defecto:" -ForegroundColor Yellow
    $response.defaultPermissions | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
    
    Write-Host "`nPermisos personalizados: $($response.customPermissions.Count)" -ForegroundColor Yellow
    if ($response.customPermissions.Count -gt 0) {
        $response.customPermissions | ForEach-Object {
            $status = if ($_.isGranted) { "✅ CONCEDIDO" } else { "❌ REVOCADO" }
            Write-Host "  - $($_.permission) $status" -ForegroundColor Gray
        }
    } else {
        Write-Host "  (ninguno)" -ForegroundColor Gray
    }
    
    # Paso 3: Actualizar permisos del rol VIEWER
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "PASO 3: AGREGAR PERMISO PERSONALIZADO" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Vamos a agregar el permiso 'traffic:create' al rol VIEWER" -ForegroundColor White
    
    $updateBody = @{
        permissions = @(
            @{
                permission = "traffic:create"
                isGranted = $true
            }
        )
    } | ConvertTo-Json -Depth 3
    
    Write-Host "`nActualizando..." -ForegroundColor Yellow
    $updateResponse = Invoke-RestMethod -Uri "$baseUrl/admin/roles/VIEWER/permissions/" -Method POST -Headers $headers -Body $updateBody
    
    Write-Host "✅ $($updateResponse.message)" -ForegroundColor Green
    
    # Paso 4: Verificar cambios
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "PASO 4: VERIFICAR CAMBIOS" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    
    $response2 = Invoke-RestMethod -Uri "$baseUrl/admin/roles/VIEWER/permissions/" -Method GET -Headers $headers
    
    Write-Host "Permisos personalizados actuales:" -ForegroundColor Yellow
    $response2.customPermissions | ForEach-Object {
        $status = if ($_.isGranted) { "✅" } else { "❌" }
        Write-Host "  $status $($_.permission) (otorgado por: $($_.grantedBy))" -ForegroundColor Gray
    }
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "✅ PRUEBA COMPLETADA EXITOSAMENTE" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ ERROR:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $errorBody = $reader.ReadToEnd()
        Write-Host "`nDetalles del error:" -ForegroundColor Yellow
        Write-Host $errorBody -ForegroundColor Gray
    }
}

Write-Host "`nPresiona cualquier tecla para salir..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
