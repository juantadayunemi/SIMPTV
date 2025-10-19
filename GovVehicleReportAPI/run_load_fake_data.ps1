# Ejecuta el management command load_fake_data en el microservicio GovVehicleReportAPI
# Uso: desde la raíz del proyecto ejecutar: .\run_load_fake_data.ps1

if (Test-Path .\.venv\Scripts\Activate.ps1) {
    Write-Host "Activando entorno virtual .venv"
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "No se encontró .venv en el proyecto. Se usará el python del sistema."
}

Write-Host "Ejecutando: python manage.py load_fake_data"
python manage.py load_fake_data

if ($LASTEXITCODE -eq 0) {
    Write-Host "Datos falsos cargados correctamente"
} else {
    Write-Host "Error al cargar datos falsos (exit code: $LASTEXITCODE)"
}
