# ⚡️ Instrucciones rápidas para auto-recuperación de modelos

1. Si eliminas o corrompes cualquier archivo de modelo en `apps/entities/models/`, no edites manualmente los imports en `__init__.py`.
2. Ejecuta:

    ```bash
    python manage.py generate_entities --organized
    ```

3. El generador comentará automáticamente los bloques de importación problemáticos, recreará los archivos eliminados y restaurará los imports.
4. El sistema es auto-recuperable y robusto ante eliminaciones accidentales.

---
# Auto-recuperación de modelos y manejo de imports

Este proyecto utiliza un generador inteligente para sincronizar los modelos Django con las interfaces TypeScript de `shared/src/entities`.

## ¿Qué ocurre si eliminas un archivo de modelo?

Si eliminas manualmente un archivo de modelo (por ejemplo, `plates.py`), los bloques de importación correspondientes en `apps/entities/models/__init__.py` pueden causar errores de importación.

**Solución automática:**

El generador (`python manage.py generate_entities --organized`) detecta los archivos faltantes y comenta automáticamente los bloques de importación relacionados. Luego, recrea los archivos eliminados y restaura los imports.

## Pasos para regenerar y auto-recuperar modelos

1. Elimina o corrompe cualquier archivo de modelo en `apps/entities/models/`.
2. Ejecuta:

    ```bash
    python manage.py generate_entities --organized
    ```

3. El generador comentará los imports problemáticos, recreará los archivos y restaurará los imports.

## Notas

- No es necesario editar manualmente los imports en `__init__.py`.
- El sistema es auto-recuperable y robusto ante eliminaciones accidentales.

---
# 🛠️ Generador de Modelos DLL desde TypeScript

### Comando: `python manage.py generate_entities`

Este comando genera automáticamente los modelos DLL de Django a partir de las interfaces TypeScript ubicadas en el proyecto compartido (`shared/src/entities`).

**¿Para qué sirve?**
- Convierte las interfaces TypeScript en modelos abstractos de Django (DLL), listos para ser heredados en otras apps.
- Permite mantener sincronizados los modelos entre backend y frontend, facilitando el desarrollo ágil y la integración continua.
- Sobrescribe los modelos cada vez que se ejecuta, ideal para entornos de desarrollo con cambios frecuentes.

**¿Cómo funciona?**
1. Busca todos los archivos TypeScript en la ruta compartida (`shared/src/entities`).
2. Analiza las interfaces y sus propiedades, mapeando los tipos TypeScript a campos Django:
    - `id: number` → campo autoincremental (identity, heredado de BaseModel)
    - `id: string` o `guid: string` → campo `UUIDField` autogenerado
    - `createdAt`, `updatedAt` → `DateTimeField` (en migraciones SQL Server se recomienda default `getdate()`)
    - Otros tipos (`string`, `number`, `boolean`, arrays, enums) se mapean automáticamente
3. Genera los archivos de modelos en la carpeta `apps/entities/models/` organizados por dominio (auth, traffic, plates, etc).
4. Genera los archivos de constantes y choices en `apps/entities/constants/`.
5. Sobrescribe los modelos existentes (no es necesario borrar manualmente).

**Opciones avanzadas:**
- `--shared-path`: Ruta al proyecto compartido TypeScript (por defecto: `../shared/src`)
- `--entities-only`: Solo genera modelos, omite tipos/enums
- `--organized`: Genera estructura organizada por dominio (recomendado)
- `--output-file`: Archivo de salida para modelos (por defecto: `apps/entities/models.py`)
- `--dry-run`: Muestra el resultado sin escribir archivos

**Ejemplo de uso básico:**
```bash
python manage.py generate_entities --organized
```

**Ejemplo de uso avanzado:**
```bash
python manage.py generate_entities --shared-path="../shared/src" --entities-only --dry-run
```

**Notas técnicas:**
- El campo `id` siempre es autoincremental (identity) y heredado de `BaseModel`.
- Los GUIDs se generan como `UUIDField` con autogeneración.
- Los campos de fecha (`createdAt`, `updatedAt`) deben tener default `getdate()` en migraciones SQL Server (personalizar si es necesario).
- Los modelos generados son abstractos y no crean tablas directamente, deben ser heredados en apps concretas.

# Urbia Traffic Analysis API Backend

Backend API REST completo construido con **Django 5.2** + **Django REST Framework** para sistema de análisis de tráfico vehicular con IA y Machine Learning.

## 🚀 Características Principales

- **Django 5.2** + **Django REST Framework 3.15** 
- **Autenticación JWT Bearer Token** con djangorestframework-simplejwt
- **Base de datos SQL Server** (mssql-django) con fallback a SQLite para desarrollo
- **Arquitectura modular** con apps separadas para trabajo en equipo
- **Configuración por entornos** (development/production)
- **API REST pura** (sin templates, solo JSON responses)
- **Preparado para OpenCV**, **YOLO**, **ML/AI** y **notificaciones en tiempo real**

## 📁 Estructura del Proyecto

```
backend/
├── venv/                          # Entorno virtual Python 3.13
├── config/                        # Configuración Django
│   ├── settings/
│   │   ├── base.py               # Settings compartidos
│   │   ├── development.py        # Settings desarrollo
│   │   └── production.py         # Settings producción
│   ├── urls.py                   # URLs principales
│   ├── wsgi.py
│   └── asgi.py
├── apps/                         # Apps Django modulares
│   ├── shared_models/           # ✅ Modelos base (Usuario, TrafficEntity, VehicleDetection)
│   ├── authentication/          # 🔄 JWT tokens, usuarios, roles
│   ├── traffic_analysis/        # 🔄 OpenCV, análisis de tráfico
│   ├── plate_detection/         # 🔄 YOLO, detección de placas
│   ├── traffic_prediction/      # 🔄 ML, análisis predictivo
│   ├── external_apis/           # 🔄 APIs externas infracciones
│   └── notifications/           # 🔄 Email, WhatsApp, WebSockets
├── requirements/                # Requirements organizados
│   ├── base.txt                 # ✅ Dependencias base
│   ├── development.txt          # ✅ Dependencias desarrollo
│   └── production.txt           # ✅ Dependencias producción
├── logs/                        # Logs del sistema
├── media/                       # Archivos subidos
├── manage.py                    # ✅ Configurado para development
├── .env.example                 # ✅ Variables de entorno ejemplo
├── .gitignore                   # ✅ Gitignore completo
└── README.md                    # ✅ Este archivo
```

**Leyenda**: ✅ Implementado | 🔄 Preparado para implementar

## ⚡ Quick Start

### 1. Prerrequisitos
- Python 3.12+ (Probado con Python 3.13)
- Git

### 2. Configuración Inicial

```bash
# Clonar y navegar al proyecto
cd backend/

# El entorno virtual ya está creado y activado
# Si necesitas reactivarlo:
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac

# Las dependencias ya están instaladas
# Si necesitas reinstalar:
# pip install -r requirements/base.txt
```

### 3. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
copy .env.example .env  # Windows
# cp .env.example .env    # Linux/Mac

# Editar .env con tus configuraciones
```

### 4. Ejecutar Migraciones (Ya ejecutadas)

```bash
# Las migraciones ya están aplicadas
# Si necesitas recrear:
# python manage.py makemigrations
# python manage.py migrate
```

### 5. Iniciar Servidor

```bash
# Activar entorno virtual (si no está activo)
.\venv\Scripts\Activate.ps1

# Iniciar servidor de desarrollo
python manage.py runserver

# El API estará disponible en: http://127.0.0.1:8000/
```

## 🔧 Configuración por Entornos

### Desarrollo (Actual)
- **Base de datos**: SQLite (db.sqlite3)
- **Debug**: Activado
- **CORS**: Permitir todos los orígenes
- **Configuración**: `config.settings.development`

### Producción
- **Base de datos**: SQL Server (mssql-django)
- **Debug**: Desactivado
- **Seguridad**: Headers de seguridad activados
- **Configuración**: `config.settings.production`

## 📡 Endpoints Disponibles

### API Root
- `GET /` - Información de la API y endpoints disponibles

### Admin
- `GET /admin/` - Panel de administración Django

### Modelos Implementados
Los siguientes modelos están disponibles en el admin:
- **Usuario personalizado** con roles (admin, operator, viewer)
- **TrafficEntity** - Entidades de tráfico con geolocalización
- **VehicleDetection** - Detecciones de vehículos con confidence score

## 🔐 Autenticación JWT

El sistema está configurado para usar JWT Bearer Tokens:

```python
# En settings configurado:
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

## 🗄️ Base de Datos

### SQLite (Desarrollo - Actual)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### SQL Server (Producción)
```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='1433'),
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes;',
        },
    }
}
```

## 📦 Dependencias Principales

### Base (Ya instaladas)
- Django 5.2
- Django REST Framework 3.15.2
- djangorestframework-simplejwt 5.3.0
- mssql-django 1.6
- pyodbc >= 3.0
- python-decouple 3.8
- django-cors-headers 4.4.0

### Desarrollo (Ya instaladas)
- django-extensions 4.1

## 🔮 Preparado para Futuras Implementaciones

### OpenCV + Análisis de Tráfico
```bash
pip install opencv-python opencv-contrib-python
```

### YOLO + Detección de Placas
```bash
pip install ultralytics
```

### Machine Learning
```bash
pip install scikit-learn tensorflow pandas numpy
```

### Notificaciones en Tiempo Real
```bash
pip install celery redis channels channels-redis
pip install sendgrid twilio  # Email y WhatsApp
```

## 🧪 Testing

```bash
# Instalar dependencias de testing
pip install -r requirements/development.txt

# Ejecutar tests (cuando se implementen)
python manage.py test

# Linting y formateo
black .
flake8 .
```

## 🚀 Despliegue

### Variables de Entorno Requeridas (Producción)
```env
SECRET_KEY=tu-clave-secreta-muy-segura
DEBUG=False
DB_NAME=UrbiaTrafficDb
DB_USER=tu_usuario_sql_server
DB_PASSWORD=tu_password_sql_server
DB_HOST=tu_host_sql_server
DB_PORT=1433
```

## 🤝 Contribución

1. Las apps están preparadas para desarrollo modular
2. Cada app tendrá su propio `models.py`, `serializers.py`, `views.py`, `urls.py`
3. Los services se organizan en carpetas `services/`
4. Se siguen las mejores prácticas de Django REST Framework

## 🔧 Comandos Útiles

```bash
# Crear nueva app
python manage.py startapp nombre_app

# Crear superusuario
python manage.py createsuperuser

# Shell interactivo
python manage.py shell

# Recolectar archivos estáticos
python manage.py collectstatic

# Ver configuración actual
python manage.py diffsettings
```

## ⚠️ Notas Importantes

1. **El servidor está ejecutándose correctamente** en desarrollo con SQLite
2. **Las migraciones están aplicadas** y los modelos funcionan
3. **El admin está configurado** para gestionar usuarios y entidades de tráfico
4. **JWT está configurado** pero los endpoints de autenticación se implementarán en `authentication` app
5. **Preparado para SQL Server** cambiando `USE_SQLITE=False` en .env
6. **Arquitectura modular** permite desarrollo en equipo por apps independientes

## 🎯 Próximos Pasos

1. Implementar app `authentication` con endpoints JWT
2. Implementar app `traffic_analysis` con OpenCV
3. Implementar app `plate_detection` con YOLO
4. Implementar app `traffic_prediction` con ML
5. Implementar app `external_apis` para consultas externas
6. Implementar app `notifications` con WebSockets
7. Convertir modelos del proyecto `shared/src/entities`

---

**Estado Actual**: ✅ Backend base funcional con Django 5.2 + DRF + modelos de prueba + migraciones aplicadas + servidor corriendo

**Desarrollado para**: Sistema de análisis de tráfico vehicular con IA 🚗🤖