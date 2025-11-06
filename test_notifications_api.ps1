# Script para probar la API de notificaciones
# Asegúrate de tener un token de acceso válido

$token = Read-Host "Ingresa tu access_token (desde localStorage del navegador)"

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Write-Host "`n🔍 Probando endpoint de notificaciones..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/notifications/notifications/" -Headers $headers -Method Get
    
    Write-Host "`n✅ Respuesta exitosa:" -ForegroundColor Green
    Write-Host "📊 Total: $($response.count)" -ForegroundColor Yellow
    Write-Host "📄 Resultados: $($response.results.Count)" -ForegroundColor Yellow
    
    if ($response.results.Count -gt 0) {
        Write-Host "`n📋 Primera notificación:" -ForegroundColor Cyan
        $response.results[0] | ConvertTo-Json -Depth 5
    }
    
} catch {
    Write-Host "`n❌ Error:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $errorBody = $reader.ReadToEnd()
        Write-Host "Detalles: $errorBody" -ForegroundColor Red
    }
}
