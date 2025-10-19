# GovVehicleReportAPI

A small Django microservice that simulates a government vehicle-report API. It uses SQLite and exposes a simple endpoint to query vehicle reports by license plate.

Quick start:

- Create a venv and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Run migrations and load fake data:

```powershell
python manage.py migrate
python manage.py loaddata
python manage.py load_fake_data
```

- Run server (use port 7000 to avoid conflict with main API):

```powershell
python manage.py runserver 7000
```

- Or run the provided helper script on Windows PowerShell:

```powershell
```markdown
# GovVehicleReportAPI

Microservicio Django pequeño que simula una API de denuncias/vehículos (SQLite).

Resumen rápido — qué hay y para qué sirve
- `gov_vehicle_report/`: configuración del proyecto Django (settings, urls, wsgi).
- `vehicles/`: app que contiene los modelos `Vehicle` y `Denuncia`, las vistas y el comando de carga de datos.
- `manage.py`: gestor de Django; está preparado para leer `.env` y usar `PORT` como puerto por defecto.
- `load_fake_data` (si está presente): comando que inserta datos de prueba en la base de datos.
- `runserver.ps1` y `run_load_fake_data.ps1`: scripts PowerShell que facilitan levantar el servidor y cargar datos, leen `.env` para centralizar el puerto.

Preparar y ejecutar (Windows PowerShell)

1) Crear entorno virtual e instalar dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Configurar puerto centralizado (opcional):

- Edita `.env` en la raíz del microservicio y cambia `PORT` si quieres otro puerto.

```text
PORT=7000
```

3) Aplicar migraciones y cargar datos de prueba:

```powershell
python manage.py migrate
python manage.py load_fake_data    # o usar .\run_load_fake_data.ps1
```

4) Levantar servidor (usa el puerto centralizado en `.env`):

```powershell
python manage.py runserver       # usa PORT de .env o 7000 por defecto
# o usar el wrapper que activa el venv y respeta .env
.\runserver.ps1
```

5) Probar la API (ejemplo):

```powershell
.\test_api.ps1 -placa ABC123
# o con curl / Invoke-RestMethod a http://localhost:<PORT>/api/vehicle?placa=ABC123
```

Notas importantes
- Si eliminaste el comando `load_fake_data` de la carpeta `management/commands`, las instrucciones anteriores para cargar datos ya no aplicarán; en ese caso usa otro mecanismo (fixtures o scripts en `scripts/`).
- `gov_vehicle_report` contiene la configuración del proyecto Django (equivalente a la carpeta `project/`), mientras que `vehicles` es la app concreta con modelos y vistas. Mantener esa separación es la convención de Django.


``` 

-- Resumen corto (comandos esenciales) --

- Crear venv e instalar:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Configurar puerto en `.env` (opcional, por defecto 7000):

```text
PORT=7000
```

- Migrar y cargar datos de prueba:

```powershell
python manage.py migrate
python manage.py load_fake_data   # si existe
```

- Ejecutar servidor (usa `.env`):

```powershell
python manage.py runserver
# o
.\runserver.ps1
```

- Probar API:

```powershell
.\test_api.ps1 -placa ABC123
```

