# 🧪 Guía de Testing End-to-End - Sistema de Análisis de Tráfico

## ✅ Implementación Completada

### Backend (100%)
- ✅ API Endpoint: `POST /api/traffic/analyze-video/`
- ✅ WebSocket Consumer: `/ws/traffic/analysis/{id}/`
- ✅ Celery Task con eventos WebSocket
- ✅ VideoProcessor con datos completos
- ✅ Models sincronizados

### Frontend (100%)
- ✅ WebSocket Service
- ✅ VideoUpload Component
- ✅ AnalysisProgress Component
- ✅ AnalysisResults Component
- ✅ TrafficAnalysisPage integrada

---

## 🚀 Cómo Probar el Sistema

### Prerequisitos

1. **Backend corriendo**:
```bash
cd backend

# Terminal 1: Django
python manage.py runserver

# Terminal 2: Celery Worker
celery -A config worker --loglevel=info --pool=solo

# Terminal 3: Celery Beat (opcional)
celery -A config beat --loglevel=info
```

2. **Redis corriendo**:
```bash
# Windows con WSL
wsl redis-server

# O Docker
docker run -d -p 6379:6379 redis
```

3. **Frontend corriendo**:
```bash
cd frontend
npm run dev
```

4. **SQL Server corriendo** (ya configurado)

---

## 📝 Pasos de Testing

### 1️⃣ Preparar Datos de Prueba

#### Crear Ubicación (via Django Admin o API):
```bash
POST http://localhost:8000/api/traffic/locations/
{
  "description": "Intersección Principal",
  "latitude": -12.046374,
  "longitude": -77.042793,
  "city": "Lima",
  "province": "Lima",
  "country": "PE",
  "isActive": true
}
```

#### Crear Cámara:
```bash
POST http://localhost:8000/api/traffic/cameras/
{
  "name": "Cámara Norte",
  "locationId": 1,
  "lanes": 2,
  "coversBothDirections": false,
  "isActive": true
}
```

### 2️⃣ Probar desde Frontend

1. **Abrir navegador**: http://localhost:5173/traffic/analysis

2. **Subir video**:
   - Arrastra un archivo MP4 o selecciona desde el explorador
   - Videos de prueba recomendados:
     - Tráfico urbano (30-60 segundos)
     - Buena iluminación
     - Vehículos claramente visibles

3. **Seleccionar cámara**: 
   - Elige "Cámara Norte"
   - La ubicación se auto-rellena

4. **Iniciar análisis**:
   - Click en "Start Analysis"
   - Deberías ver:
     - ✅ Barra de progreso actualizándose
     - ✅ Contador de vehículos incrementando
     - ✅ Logs en tiempo real

5. **Esperar resultados**:
   - Cuando termine (100%):
     - ✅ Tarjetas de resumen
     - ✅ Gráfico de distribución por tipo
     - ✅ Estadísticas detalladas

---

## 🔍 Verificaciones de Consola

### Frontend Console (DevTools)

Deberías ver:
```
🔌 Conectando a WebSocket: ws://localhost:8000/ws/traffic/analysis/1/
✅ WebSocket conectado
📨 Mensaje recibido [progress_update]: { processed_frames: 30, total_frames: 900, ... }
📨 Mensaje recibido [vehicle_detected]: { track_id: "abc123", vehicle_type: "car", ... }
📨 Mensaje recibido [processing_complete]: { analysis_id: 1, total_vehicles: 15, ... }
```

### Backend Console (Django)

Deberías ver:
```
✅ Video guardado: traffic_videos/20251010_143045_test.mp4
✅ TrafficAnalysis creado: ID=1
✅ Celery task iniciado: abc-def-ghi-123
🔌 Cliente conectando a análisis 1
✅ Cliente conectado a grupo traffic_analysis_1
📹 Iniciando procesamiento de video: /path/to/video.mp4
📊 Video info: 1920x1080, 30 FPS, 900 frames
🚗 Vehículo detectado: car (confidence: 0.92)
✅ Análisis completado exitosamente
```

### Celery Worker Console

Deberías ver:
```
[INFO/MainProcess] Task apps.traffic_app.tasks.process_video_analysis[abc-def-ghi] received
[INFO/MainProcess] Starting video analysis task for ID: 1
[INFO/MainProcess] Video analysis completed successfully for ID: 1
[INFO/MainProcess] Task apps.traffic_app.tasks.process_video_analysis[abc-def-ghi] succeeded
```

---

## 🗄️ Verificaciones de Base de Datos

### SQL Server Management Studio

```sql
-- Ver análisis creado
SELECT * FROM traffic_analyses WHERE id = 1;

-- Ver vehículos detectados
SELECT id, vehicleType, confidence, firstDetectedAt, lastDetectedAt
FROM traffic_vehicles
WHERE trafficAnalysisId = 1;

-- Contar vehículos por tipo
SELECT vehicleType, COUNT(*) as count
FROM traffic_vehicles
WHERE trafficAnalysisId = 1
GROUP BY vehicleType;

-- Ver frames guardados
SELECT vehicleId, frameNumber, frameQuality, confidence
FROM traffic_vehicle_frames
WHERE vehicleId IN (
    SELECT id FROM traffic_vehicles WHERE trafficAnalysisId = 1
)
ORDER BY frameQuality DESC;
```

**Validaciones**:
- ✅ `traffic_analyses.status = 'COMPLETED'`
- ✅ `traffic_analyses.totalVehicles > 0`
- ✅ `traffic_vehicles` tiene registros con CUID en `id`
- ✅ `firstDetectedAt` y `lastDetectedAt` son timestamps válidos
- ✅ `confidence` es decimal entre 0 y 1
- ✅ `traffic_vehicle_frames` tiene `boundingBoxX/Y/Width/Height` poblados
- ✅ `frameQuality` es decimal entre 0 y 1

---

## 🐛 Troubleshooting

### Problema: WebSocket no conecta

**Síntomas**: Frontend muestra "Failed to connect"

**Soluciones**:
1. Verificar que Django corre con ASGI:
   ```bash
   # En lugar de runserver, usar:
   daphne config.asgi:application --port 8000 --bind 0.0.0.0
   ```

2. Verificar CORS y ALLOWED_HOSTS en settings.py:
   ```python
   ALLOWED_HOSTS = ['localhost', '127.0.0.1']
   CORS_ALLOWED_ORIGINS = ['http://localhost:5173']
   ```

### Problema: Celery no procesa

**Síntomas**: Task queda en PENDING

**Soluciones**:
1. Verificar Redis corriendo:
   ```bash
   redis-cli ping  # Debe responder PONG
   ```

2. Verificar Celery worker activo:
   ```bash
   celery -A config inspect active
   ```

3. Ver logs de Celery:
   ```bash
   celery -A config worker --loglevel=debug
   ```

### Problema: Video no se procesa

**Síntomas**: Task falla con error

**Soluciones**:
1. Verificar que YOLOv8 está instalado:
   ```bash
   pip install ultralytics
   ```

2. Verificar que el video existe:
   ```python
   import os
   os.path.exists('media/traffic_videos/xxx.mp4')
   ```

3. Verificar permisos de escritura en `media/`

### Problema: Frontend no muestra progreso

**Síntomas**: Barra de progreso no se actualiza

**Soluciones**:
1. Abrir DevTools Console, verificar mensajes WebSocket
2. Verificar que `VITE_WS_URL` esté configurado:
   ```env
   VITE_WS_URL=localhost:8000
   ```
3. Refrescar página (F5)

---

## ✅ Checklist de Testing Completo

### Funcionalidad Básica
- [ ] Puedo subir un video
- [ ] Puedo seleccionar cámara/ubicación
- [ ] El botón "Start Analysis" se activa
- [ ] El video se sube correctamente

### Procesamiento
- [ ] Celery task se ejecuta
- [ ] VideoProcessor detecta vehículos
- [ ] Frames se procesan secuencialmente
- [ ] No hay errores en consola

### WebSocket Real-time
- [ ] WebSocket conecta exitosamente
- [ ] Recibo eventos `progress_update`
- [ ] Recibo eventos `vehicle_detected`
- [ ] Recibo evento `processing_complete`
- [ ] Logs se actualizan en tiempo real

### UI Frontend
- [ ] Barra de progreso se actualiza
- [ ] Contador de vehículos incrementa
- [ ] Logs aparecen en el panel
- [ ] Al finalizar, muestra resultados
- [ ] Tarjetas de resumen correctas
- [ ] Gráfico de distribución correcto

### Base de Datos
- [ ] TrafficAnalysis creado con status COMPLETED
- [ ] Vehicles guardados con CUID
- [ ] VehicleFrames guardados con bbox
- [ ] Timestamps correctos
- [ ] Confidence y quality en rango [0,1]
- [ ] Foreign keys funcionando

### Performance
- [ ] Procesamiento no excede 2x duración del video
- [ ] UI responde durante procesamiento
- [ ] No hay memory leaks
- [ ] WebSocket no se desconecta

---

## 📊 Métricas Esperadas

Para un video de **30 segundos a 30 FPS** (900 frames):

| Métrica | Valor Esperado |
|---------|----------------|
| Tiempo de procesamiento | 60-90 segundos |
| Vehículos detectados | 5-20 |
| Frames procesados | 900 (skip_frames=0) o ~300 (skip_frames=2) |
| Frames guardados por vehículo | 3-10 (FRAMES_PER_VEHICLE) |
| Tamaño DB | ~1-5 MB |
| Uso RAM | ~500 MB - 1 GB |

---

## 🎉 Test Exitoso Si...

1. ✅ Video se procesa completamente sin errores
2. ✅ Frontend muestra progreso en tiempo real
3. ✅ Resultados aparecen al 100%
4. ✅ Base de datos tiene datos correctos
5. ✅ Puedo hacer "New Analysis" y repetir

---

## 📹 Video de Prueba Recomendado

**Características ideales**:
- Formato: MP4 (H.264)
- Duración: 30-60 segundos
- Resolución: 720p o 1080p
- FPS: 25-30
- Contenido: Tráfico urbano con 5-10 vehículos visibles
- Iluminación: Día/buena visibilidad

**Descargar videos de prueba**:
- https://www.pexels.com/search/videos/traffic/
- https://pixabay.com/videos/search/traffic/

---

## 🚨 Errores Comunes y Soluciones

### "ModuleNotFoundError: No module named 'celery'"
```bash
pip install celery redis
```

### "Connection refused" (Redis)
```bash
# Instalar Redis
# Windows: https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt install redis-server
```

### "Cannot connect to WebSocket"
```bash
# Usar Daphne en lugar de runserver
pip install daphne
daphne config.asgi:application
```

### "Video file not found"
```python
# Verificar MEDIA_ROOT en settings.py
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Crear directorio si no existe
os.makedirs(MEDIA_ROOT, exist_ok=True)
```

---

## 🎯 Siguiente Nivel (Opcional)

Una vez que el testing básico funciona:

1. **Probar con videos largos** (5+ minutos)
2. **Probar con múltiples clientes WebSocket** (varias pestañas)
3. **Probar con diferentes condiciones** (noche, lluvia, etc.)
4. **Agregar tests unitarios** con pytest
5. **Agregar tests de integración** con Selenium
6. **Setup CI/CD** con GitHub Actions

---

## 📞 Soporte

Si encuentras problemas:
1. Revisar logs de Django, Celery y Frontend console
2. Verificar que todos los servicios estén corriendo
3. Revisar este documento de troubleshooting
4. Documentar el error con screenshots y logs

**¡El sistema está 100% implementado y listo para testing!** 🎉
