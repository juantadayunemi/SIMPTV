# 🚀 TrafiSmart - Guía de Instalación y Configuración

## 📋 Requisitos Previos

### Software Obligatorio
- **Python 3.13** o superior
- **Node.js 18+** y npm
- **SQL Server** (2019 o superior) o **SQL Server Express**
- **Redis** (para Celery y WebSocket)
- **Git**

### Drivers y Herramientas
- **ODBC Driver 18 for SQL Server** - [Descargar aquí](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- **FFmpeg** (opcional, para procesamiento de video) - [Descargar aquí](https://ffmpeg.org/download.html)

---

## 🔧 Instalación del Backend

### 1. Clonar el Repositorio
```bash
git clone https://github.com/juantadayunemi/SIMPTV.git
cd SIMPTV
```

### 2. Crear Entorno Virtual
```bash
cd backend
python -m venv venv
```

### 3. Activar Entorno Virtual

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.\venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar Dependencias
```bash
pip install -r requirements_production.txt
```

**⚡ Para GPU (CUDA 12.1) - Opcional pero recomendado:**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### 5. Configurar Variables de Entorno

Crear archivo **`.env`** en `backend/`:

```env
# Database Configuration
DB_NAME=TrafiSmartDB
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=1433
DB_DRIVER=ODBC Driver 18 for SQL Server

# Django Security
SECRET_KEY=tu-clave-secreta-aqui-genera-una-nueva
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_app

# YOLO Configuration
YOLO_MODEL_PATH=yolov8n.pt
YOLO_CONFIDENCE=0.5
```

### 6. Crear Base de Datos

En SQL Server Management Studio o Azure Data Studio:

```sql
CREATE DATABASE TrafiSmartDB;
GO
```

### 7. Aplicar Migraciones
```bash
python manage.py migrate
```

### 8. Crear Superusuario
```bash
python manage.py createsuperuser
```

### 9. Iniciar Servicios

**Terminal 1 - Django API (puerto 8000):**
```bash
python manage.py runserver
```

**Terminal 2 - Daphne WebSocket (puerto 8001):**
```bash
daphne -b 0.0.0.0 -p 8001 config.asgi:application
```

**Terminal 3 - Celery Worker:**
```bash
celery -A config worker --loglevel=info --pool=solo
```

**Terminal 4 - Redis (si no está instalado como servicio):**
```bash
redis-server
```

---

## 🎨 Instalación del Frontend

### 1. Instalar Dependencias
```bash
cd frontend
npm install
```

### 2. Configurar Variables de Entorno

Crear archivo **`.env`** en `frontend/`:

```env
# Backend API
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=localhost:8001

# App Configuration
VITE_APP_NAME="Sistema de Análisis de Tráfico"
VITE_MAX_FILE_SIZE=10485760

# Development
VITE_DEBUG=true
```

### 3. Iniciar Servidor de Desarrollo
```bash
npm run dev
```

El frontend estará disponible en: **http://localhost:5173**

---

## 📦 Instalación de Redis en Windows

### Opción 1: Redis Portable (Más Fácil)
1. Descargar desde: https://github.com/tporadowski/redis/releases
2. Extraer en `C:\Redis`
3. Ejecutar: `redis-server.exe`

### Opción 2: Memurai (Redis Compatible)
1. Descargar desde: https://www.memurai.com/
2. Instalar como servicio de Windows
3. Se inicia automáticamente

### Opción 3: Docker (Recomendado para equipos)
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

---

## 🧪 Verificación de Instalación

### 1. Verificar Backend
```bash
curl http://localhost:8000/api/auth/login/
```
Debe retornar: `{"detail":"Method \"GET\" not allowed."}`

### 2. Verificar WebSocket
En PowerShell:
```powershell
Test-NetConnection -ComputerName localhost -Port 8001
```
Debe mostrar: `TcpTestSucceeded : True`

### 3. Verificar Redis
```bash
redis-cli ping
```
Debe retornar: `PONG`

### 4. Verificar Celery
En el terminal de Celery debe aparecer:
```
[tasks]
  . apps.traffic_app.tasks.process_video_analysis
  . apps.traffic_app.tasks.cleanup_old_analyses
  . apps.traffic_app.tasks.generate_analysis_report
```

---

## 🚗 Uso del Sistema

### 1. Iniciar Sesión
- Ir a: http://localhost:5173/login
- Usar credenciales del superusuario

### 2. Crear Ubicación
- Ir a: **Traffic → Cameras**
- Click en **"Agregar nueva cámara"**
- Ingresar coordenadas GPS (latitud/longitud)
- Guardar ubicación

### 3. Crear Cámara
- Seleccionar la ubicación creada
- Ingresar nombre, marca, modelo, etc.
- Guardar cámara

### 4. Analizar Video
- Ir a: **Traffic → Analysis**
- Subir video de tráfico (MP4, AVI, MOV)
- Seleccionar cámara
- Click en **"Start Analysis"**
- Ver progreso en tiempo real

---

## 🐛 Solución de Problemas

### Error: "Redis connection refused"
- Verificar que Redis esté corriendo: `redis-cli ping`
- Reiniciar Redis: `redis-server`

### Error: "ODBC Driver not found"
- Instalar ODBC Driver 18 para SQL Server
- Actualizar `DB_DRIVER` en `.env`

### Error: "Port 5173 already in use"
- Matar proceso: `npx kill-port 5173`
- O usar puerto alternativo: `npm run dev -- --port 5174`

### Error: "WebSocket connection failed"
- Verificar Daphne corriendo en puerto 8001
- Verificar `VITE_WS_URL` en frontend `.env`
- Verificar CORS en backend `settings.py`

### Error: "Celery task timeout"
- Aumentar timeout en `tasks.py`
- Verificar que YOLO model esté descargado
- Revisar logs en terminal de Celery

---

## 📊 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│  React + TypeScript + Vite (Port 5173/5174)               │
│  - Upload videos                                           │
│  - Real-time WebSocket connection                          │
│  - Display results and statistics                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Django)                         │
├─────────────────────────────────────────────────────────────┤
│  Django API (Port 8000)        │  Daphne WebSocket (8001)  │
│  - REST API endpoints          │  - Real-time updates       │
│  - Authentication (JWT)        │  - Progress notifications  │
│  - Video upload                │  - Vehicle detection logs  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   CELERY WORKER                             │
│  - Asynchronous video processing                           │
│  - YOLOv8 object detection                                 │
│  - Deep SORT vehicle tracking                              │
│  - EasyOCR license plate recognition                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              REDIS (Message Broker)                         │
│  - Celery task queue (Port 6379)                          │
│  - WebSocket channel layer                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              SQL SERVER (Database)                          │
│  - Users, Cameras, Locations                               │
│  - Traffic Analyses                                        │
│  - Vehicles and Frames                                     │
│  - License Plates                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Comandos Útiles

### Backend
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Regenerar entidades desde TypeScript
python manage.py generate_entities

# Iniciar shell de Django
python manage.py shell

# Limpiar análisis antiguos
python manage.py cleanup_old_analyses --days 30
```

### Frontend
```bash
# Instalar dependencias
npm install

# Iniciar desarrollo
npm run dev

# Build para producción
npm run build

# Preview build
npm run preview
```

### Celery
```bash
# Iniciar worker (Windows)
celery -A config worker --loglevel=info --pool=solo

# Iniciar worker (Linux/Mac)
celery -A config worker --loglevel=info

# Ver tareas activas
celery -A config inspect active

# Ver tareas registradas
celery -A config inspect registered
```

---

## 👥 Equipo de Desarrollo

Para dudas o soporte, contactar a:
- **Juan Tadayu** - juantadaymalan3@gmail.com

---

## 📄 Licencia

Este proyecto es privado y confidencial. Todos los derechos reservados.

---

**Última actualización:** 10 de Octubre, 2025
