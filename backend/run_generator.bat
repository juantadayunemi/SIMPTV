@echo off
echo 🚀 Activando entorno virtual y ejecutando generador...

REM Buscar entorno virtual
if exist "venv\Scripts\activate.bat" (
    echo 🐍 Activando entorno virtual: venv
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo 🐍 Activando entorno virtual: .venv
    call .venv\Scripts\activate.bat
) else if exist "env\Scripts\activate.bat" (
    echo 🐍 Activando entorno virtual: env
    call env\Scripts\activate.bat
) else if exist "..\venv\Scripts\activate.bat" (
    echo 🐍 Activando entorno virtual: ..\venv
    call ..\venv\Scripts\activate.bat
) else if exist "..\.venv\Scripts\activate.bat" (
    echo 🐍 Activando entorno virtual: ..\.venv
    call ..\.venv\Scripts\activate.bat
) else (
    echo ⚠️  No se encontró entorno virtual
    echo Ejecutando con Python del sistema...
)

echo.
echo 📋 Ejecutando: python manage.py generate_entities --shared-path=../shared/src --organized --dry-run
echo ============================================================

python manage.py generate_entities --shared-path=../shared/src --organized --dry-run

echo.
echo 🎯 Proceso completado
set /p continue="¿Ejecutar sin --dry-run para generar archivos reales? (y/N): "

if /i "%continue%"=="y" (
    echo.
    echo 🔧 Ejecutando generación real...
    python manage.py generate_entities --shared-path=../shared/src --organized
    echo ✅ Generación completada!
) else (
    echo 👋 Saliendo...
)

pause