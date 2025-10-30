# Ejecutar Scheduled Tasks con Celery (Windows)

## Prerequisitos
-Ejecutar Redis
-Entorno virtual activado

## Pasos para Ejecutar Run Scheduled

### Paso 1: Entrar al directorio backend y activar entorno virtual
```cmd
cd backend
venv\Scripts\activate
```

### Paso 2: Iniciar Redis Server (en terminal separado)
```cmd
.\redis-server.exe redis.windows.conf
```

### Paso 3: Iniciar Celery Worker (en terminal separado)
```cmd
celery -A config.celery worker --loglevel=info --pool=solo
```

### Paso 4: Iniciar Django Server (en terminal separado)
```cmd
celery -A config beat --loglevel=info
```
