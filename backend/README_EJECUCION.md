# 🚀 Manual de Ejecución - TrafiSmart Backend (Windows)

## 📋 Requisitos Previos

- **Windows 10/11**
- Python  3.13.5
- Redis instalado en `redis/`
- Entorno virtual creado en `venv/`

## 🏃‍♂️ Pasos para Ejecutar el Sistema en Windows

### Paso 1: Entrar al directorio backend y activar entorno virtual
```cmd
cd backend
venv\Scripts\activate
```

### Paso 2: Iniciar Redis Server (en terminal separado)
```cmd
cd redis
.\redis-server.exe redis.windows.conf
```

### Paso 3: Iniciar Celery Worker (en terminal separado)
```cmd
# PRERREQUISITOS: Redis debe estar corriendo, venv activado, estar en backend/
celery -A config worker --loglevel=info --pool=solo
```

### Paso 4: Iniciar Django Server (en terminal separado)
```cmd
# Desde el directorio backend (con venv activado)
python manage.py runserver
```

## ✅ Verificación de Servicios

### Verificar Redis
```cmd
redis-cli ping
```
Debe responder: `PONG`

### Verificar Django
Abrir navegador: `http://localhost:8000/api/traffic/`

### Verificar Celery
Debe mostrar logs como:
```
[...] celery.worker.consumer: Connected to redis://localhost:6379//
```

## 🔄 Orden de Inicio Recomendado

1. **Redis** (primero, porque es el broker)
2. **Celery Worker** (segundo, para procesar tareas)
3. **Django Server** (último, para recibir requests)

## 🛑 Para Detener Servicios

- **Redis**: Cerrar la ventana del terminal
- **Celery**: `Ctrl+C` en su terminal
- **Django**: `Ctrl+C` en su terminal

## 📁 Estructura de Archivos Importantes

```
backend/
├── manage.py              # Servidor Django
├── config/
│   ├── settings.py        # Configuración (Redis, Celery)
│   └── celery.py          # Config Celery
├── redis/
│   └── redis-server.exe   # Ejecutable Redis
└── venv/
    └── Scripts/activate   # Activador entorno virtual (Windows)
```

## 🚨 Solución de Problemas

### Error: "No module named celery"
```cmd
pip install celery redis channels channels-redis
```

### Error: Redis connection refused
- Verificar que Redis esté corriendo en puerto 6379
- Verificar que no haya firewall bloqueando el puerto

### Error: Celery no conecta
- Asegurar Redis esté iniciado antes que Celery
- Verificar configuración en `config/settings.py`

## 🎯 Endpoints Disponibles

- `POST /api/traffic/upload-chunk/` - Subir video por chunks
- `GET /api/traffic/` - Lista de análisis

## 📝 Notas

- Mantener todos los terminales abiertos mientras se usa la aplicación
- El sistema procesa videos incrementalmente a medida que llegan chunks
- Los logs de Celery muestran el progreso del análisis en tiempo real
- **Este manual es específico para Windows**