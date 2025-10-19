# GovVehicleReportAPI

Microservicio Django que simula una API gubernamental de denuncias/vehículos usando SQLite.

Resumen
--------
Este microservicio proporciona un endpoint sencillo para consultar denuncias o reportes asociados a un vehículo por su placa. Está pensado para pruebas y desarrollo local.

Contenido principal
------------------
- `gov_vehicle_report/`: configuración del proyecto Django (settings, urls, wsgi, etc.).
- `vehicles/`: aplicación que contiene los modelos principales (`Vehicle`, `Denuncia`), vistas y comandos de carga de datos.
- `manage.py`: entrada de Django; está preparada para leer un archivo `.env` y usar la variable `PORT` como puerto por defecto.
- `runserver.ps1` y `run_load_fake_data.ps1`: scripts PowerShell que facilitan levantar el servidor y cargar datos de prueba en Windows.

Requisitos
---------
- Python 3.8+ (preferible 3.10/3.11)
- Virtualenv (se usará el módulo `venv` incluido en Python)

Instalación y ejecución (Windows PowerShell)
-------------------------------------------
1. Crear y activar un entorno virtual, e instalar dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. (Opcional) Configurar el puerto en `.env` (archivo en la raíz del microservicio). Por ejemplo:

```text
PORT=7000
```

3. Aplicar migraciones y cargar datos de prueba:

```powershell
python manage.py migrate
python manage.py loaddata
python manage.py load_fake_data
# Alternativamente, use el script de ayuda:
.\run_load_fake_data.ps1
```

4. Levantar el servidor (usa el puerto definido en `.env` o 7000 por defecto):

```powershell
python manage.py runserver 7000
# o solo:
python manage.py runserver
# o use el wrapper que activa el venv y respeta .env
.\runserver.ps1
```

5. Probar la API (ejemplo):

```powershell
.\test_api.ps1 -placa ABC123
# o con Invoke-RestMethod / curl:
Invoke-RestMethod "http://localhost:7000/api/vehicle?placa=ABC123"
```

Contacto y contribuciones
-------------------------
Si deseas reportar un problema o contribuir, por favor abre un issue en el repositorio o envía un pull request con los cambios propuestos.

Licencia
--------
Este proyecto hereda la licencia del repositorio principal. Consulta el archivo `LICENSE` en la raíz del repositorio si existe.

