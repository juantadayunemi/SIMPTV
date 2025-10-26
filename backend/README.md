# 🧩 Comandos útiles para desarrollo

```bash
# Generar modelos DLL desde TypeScript
python manage.py generate_entities --organized
```

### 1. Vista Previa (Sin Cambios)
```bash
python manage.py generate_entities --organized --dry-run
```

### 2. Sincronización Completa (Recomendado)
```bash
python manage.py generate_entities --organized
```

### 3. Solo Entidades (Sin Constantes)
```bash
python manage.py generate_entities --organized --entities-only
```

# Aplicar migraciones (hacer para cada app)
python manage.py makemigrations auth_app
python manage.py makemigrations traffic_app
python manage.py makemigrations plates_app
python manage.py migrate

# Verificar sistema sin errores
python manage.py check


# Poblar usuario administrador y roles
python manage.py seed_admin



# Iniciar servidor de desarrollo
python manage.py runserver
```

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
# 🛠️ Sistema DLL de Generación Automática de Modelos

### Comando: `python manage.py generate_entities --organized`

Este sistema es el **corazón del backend**: convierte automáticamente las interfaces TypeScript del proyecto `shared/src/` en modelos Django abstractos (DLL Pattern).

**🎯 ¿Para qué sirve?**
- **Sincronización automática**: Mantiene los modelos Django sincronizados con TypeScript
- **DLL Pattern**: Genera modelos abstractos que se heredan en apps concretas
- **Desarrollo ágil**: Elimina la necesidad de escribir modelos manualmente
- **Arquitectura limpia**: Separación clara entre entidades DLL y modelos de negocio

**🔧 ¿Cómo funciona?**
1. **Escanea** todos los archivos TypeScript en `shared/src/entities/`, `shared/src/dto/`, `shared/src/models/`
2. **Convierte** 124+ interfaces TypeScript en modelos Django organizados por dominio
3. **Genera** estructura organizada:
   - `apps/entities/models/auth.py` - 9 entidades de autenticación
   - `apps/entities/models/traffic.py` - 27 entidades de tráfico  
   - `apps/entities/models/plates.py` - 26 entidades de placas
   - `apps/entities/models/predictions.py` - 6 entidades de predicciones
   - `apps/entities/models/notifications.py` - 14 entidades de notificaciones
   - `apps/entities/models/common.py` - 42+ entidades comunes
   - `apps/entities/constants/` - Constantes y Django choices
4. **Evita duplicación**: Filtra campos que ya están en `BaseModel` (`id`, `created_at`, `updated_at`, `is_active`)

**🏗️ Mapeo TypeScript → Django:**
```typescript
// TypeScript
interface UserEntity {
    id: string;              // → UUIDField(primary_key=True)  
    email: string;           // → EmailField(max_length=255)
    firstName: string;       // → CharField(max_length=255)
    isActive: boolean;       // → FILTRADO (ya está en BaseModel)
    createdAt: Date;         // → FILTRADO (ya está en BaseModel)
    role: UserRoleType;      // → CharField(choices=USER_ROLES_CHOICES)
}
```

**🚀 Opciones avanzadas:**
```bash
# Generación básica  , RECOMENDADO
python manage.py generate_entities --organized

# Solo entidades, sin tipos
python manage.py generate_entities --organized --entities-only

# Ver resultado sin escribir archivos
python manage.py generate_entities --organized --dry-run

# Ruta personalizada a TypeScript
python manage.py generate_entities --shared-path="../shared/src" --organized
```

**💡 Uso en apps concretas:**
```python
# En apps/auth_app/models.py
from apps.entities.models import UserEntity

class User(UserEntity):
    """Usuario concreto que hereda de entidad DLL"""
    # Campos adicionales específicos de autenticación
    last_login = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    
    class Meta:
        db_table = "auth_users"
```

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
│   ├── urls.py                   # URLs principales con auto-discovery
│   ├── wsgi.py
│   └── asgi.py
├── apps/                         # Apps Django modulares
│   ├── entities/                # ✅ Sistema DLL - Modelos generados desde TypeScript
│   │   ├── models/              # Modelos abstractos DLL organizados
│   │   ├── constants/           # Constantes y choices Django
│   │   ├── management/commands/ # Comando generate_entities
│   │   └── dto/                 # DTOs para serialización
│   ├── auth_app/                # ✅ JWT tokens, usuarios, roles
│   │   ├── management/commands/ # Comando seed_admin
│   │   ├── models.py            # User, UserRole (hereda de entities)
│   │   ├── views.py             # LoginView implementado
│   │   └── urls.py              # /api/auth/login/
│   ├── traffic_app/             # ✅ Análisis de tráfico y vehículos
│   │   ├── models.py            # TrafficAnalysis (hereda de entities)
│   │   ├── views.py             # ViewSets para análisis
│   │   └── urls.py              # /api/traffic/ con múltiples endpoints
│   ├── plates_app/              # ✅ Detección de placas
│   │   ├── models.py            # PlateDetection (hereda de entities)
│   │   └── views.py             # Preparado para YOLO
│   └── external_apis/           # 🔄 APIs externas infracciones
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

## 📡 Endpoints Implementados

### API Root
- `GET /` - Información de la API y endpoints disponibles con auto-discovery

### Documentación API
- `GET /api/schema/` - Esquema OpenAPI
- `GET /api/schema/swagger-ui/` - Interfaz Swagger UI
- `GET /api/schema/redoc/` - Documentación Redoc

### Admin Panel
- `GET /admin/` - Panel de administración Django

### Autenticación (/api/auth/)
- `POST /api/auth/login/` - Login JWT con email/password
- `POST /api/auth/register/` - 🔄 Registro de usuarios (preparado)
- `POST /api/auth/logout/` - 🔄 Logout (preparado)
- `POST /api/auth/refresh/` - 🔄 Refresh token (preparado)

### Análisis de Tráfico (/api/traffic/)
- `GET /api/traffic/analysis/` - Lista de análisis de tráfico
- `POST /api/traffic/analysis/` - Crear nuevo análisis
- `GET /api/traffic/analysis/{id}/` - Detalle de análisis específico
- `PUT /api/traffic/analysis/{id}/` - Actualizar análisis
- `DELETE /api/traffic/analysis/{id}/` - Eliminar análisis
- `GET /api/traffic/reports/` - Reportes de tráfico
- `POST /api/traffic/reports/` - Crear nuevo reporte
- `GET /api/traffic/monitoring/` - Monitoreo en tiempo real
- `GET /api/traffic/statistics/` - Estadísticas de tráfico
- `POST /api/traffic/upload-video/` - Subir video para análisis

### Modelos DLL Disponibles
Los siguientes modelos abstractos están disponibles para herencia:
- **UserEntity, UserRoleEntity** - Sistema de usuarios y roles
- **TrafficAnalysisEntity, VehicleEntity** - Análisis de tráfico
- **LicensePlateEntity, PlateAlertEntity** - Detección de placas
- **NotificationEntity** - Sistema de notificaciones
- **120+ entidades más** organizadas por dominio

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

1. **Sistema DLL Funcional**: Generador automático de modelos desde TypeScript operativo
2. **124+ Entidades Generadas**: Modelos organizados por dominio (auth, traffic, plates, etc.)
3. **Endpoints Implementados**: Auth login, Traffic analysis completo, auto-discovery de URLs
4. **Usuario Admin**: Comando `seed_admin` para crear admin@gmail.com / 123
5. **Base de datos**: SQLite para desarrollo, preparado para SQL Server producción
6. **Arquitectura modular**: Apps independientes que heredan de entities DLL
7. **Auto-recuperación**: Sistema robusto ante eliminaciones accidentales de archivos

## 🎯 Próximos Pasos

1. **Completar auth_app**: Implementar register, logout, refresh token
2. **Implementar plates_app**: Endpoints para detección de placas con YOLO
3. **Agregar predictions_app**: Modelos ML para predicciones de tráfico
4. **Implementar notifications**: Sistema de notificaciones en tiempo real
5. **Optimizar external_apis**: Integración con APIs externas de infracciones
6. **Preparar producción**: Migrar a SQL Server y configurar CI/CD

---

**Estado Actual**: ✅ Backend DLL completo con 124+ entidades generadas + Auth + Traffic endpoints + Auto-discovery + Usuario admin

**Desarrollado para**: Sistema de análisis de tráfico vehicular con IA 🚗🤖