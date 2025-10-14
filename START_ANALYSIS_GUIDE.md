# 🎯 Guía para Iniciar Análisis con YOLOv8 + OCR

## ✅ Estado Actual

El sistema está **99% listo**. Solo falta verificar que Celery esté corriendo para procesar el video.

## 📊 Componentes Necesarios

### 1. ✅ Backend Django (Puerto 8001)
```powershell
# Ya está corriendo
python manage.py runserver 0.0.0.0:8001
```

### 2. ⚠️ Celery Worker (Procesa videos)
```powershell
# Debe estar corriendo para que funcione el análisis
cd backend
celery -A config worker -l info --pool=solo
```

### 3. ⚠️ Redis (Broker de mensajes)
```powershell
# Celery necesita Redis para funcionar
redis-server
```

### 4. ✅ Frontend (Puerto 5174)
```powershell
# Ya está corriendo
cd frontend
npm run dev
```

## 🚀 Flujo Completo del Análisis

### 1. Usuario hace click en "Iniciar"
```typescript
// Frontend (CameraLiveAnalysisPage.tsx)
handlePlay() → trafficService.startAnalysis(analysisId)
    ↓
POST http://localhost:8001/api/traffic/analysis/4/start/
```

### 2. Backend recibe la solicitud
```python
# Backend (views.py)
@action(detail=True, methods=["post"])
def start(self, request, pk=None):
    # Valida que el video existe
    # Lanza tarea de Celery
    task = process_video_analysis.delay(analysis.id)
    # Actualiza estado
    analysis.status = "PROCESSING"
    analysis.isPlaying = True
```

### 3. Celery procesa el video
```python
# Backend (tasks.py)
@shared_task
def process_video_analysis(analysis_id):
    # Carga el video
    # Procesa con YOLOv8 + EasyOCR
    # Envía detecciones via WebSocket
```

### 4. Frontend recibe detecciones
```typescript
// Frontend (CameraLiveAnalysisPage.tsx)
wsService.on('vehicle_detected', (data) => {
    // Agrega detección al array
    setDetections(prev => [...prev, detection]);
});
```

### 5. DetectionLogPanel muestra los datos
```
13:45:23 tipo: auto, placa ABC-1234
13:45:25 tipo: camión, placa desconocida
13:45:27 tipo: moto, placa XYZ-5678
```

## 🔍 Verificar que Celery esté corriendo

### Opción 1: Ver procesos de Celery
```powershell
Get-Process | Where-Object {$_.ProcessName -like "*celery*"}
```

### Opción 2: Intentar iniciar Celery
```powershell
cd backend
celery -A config worker -l info --pool=solo
```

**Si ves este output, Celery está corriendo:**
```
-------------- celery@NombrePC v5.x.x
---- **** -----
--- * ***  * --
-- * - **** ---
- ** ---------- [config]
- ** ---------- .> app:         config:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 1 (solo)
-- ******* ---- .> task events: OFF
--- ***** -----
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . apps.traffic_app.tasks.process_video_analysis

celery@NombrePC ready.
```

## ⚠️ Si Celery NO está corriendo

### Instalar Redis (si no lo tienes)

**Windows:**
```powershell
# Descargar Redis para Windows
# https://github.com/microsoftarchive/redis/releases

# O usar el que ya está en tu proyecto
cd backend/redis
./redis-server.exe redis.windows.conf
```

**Verificar Redis:**
```powershell
redis-cli ping
# Debería responder: PONG
```

### Iniciar Celery

**En una nueva terminal PowerShell:**
```powershell
cd backend
celery -A config worker -l info --pool=solo
```

**Dejar esta terminal abierta** (Celery debe estar corriendo constantemente)

## 🧪 Probar el Análisis Completo

### 1. Verificar servicios corriendo:
```
✅ Django (8001)
✅ Frontend (5174)  
✅ Redis (6379)
⚠️ Celery Worker ← DEBE ESTAR CORRIENDO
```

### 2. En el navegador:
```
1. Ir a: http://localhost:5174/camera/2
2. Verificar que el video se muestra
3. Click en botón "▶️ Iniciar" (rojo)
4. Esperar unos segundos
```

### 3. Ver en Console (F12):
```javascript
✅ Análisis iniciado: {analysis_id: 4, task_id: "...", status: "PROCESSING"}
🔌 Conectando a WebSocket: ws://localhost:8001/ws/traffic/analysis/4/
✅ WebSocket conectado
📨 Mensaje recibido [vehicle_detected]: {...}
```

### 4. Ver en DetectionLogPanel:
```
13:45:23 tipo: auto, placa ABC-1234 conf: 95.3%
13:45:25 tipo: camión, placa desconocida conf: 87.2%
13:45:27 tipo: moto, placa XYZ-5678 conf: 92.1%
```

### 5. Ver en Terminal Celery:
```
[2025-10-13 13:45:20] Task process_video_analysis[...] received
🎥 Processing video: traffic_videos/20251013_...mp4
📊 Total frames: 1500
🚗 Vehicle detected: track_id=1, type=car, plate=ABC-1234
📡 Sending WebSocket event: vehicle_detected
```

## 🐛 Troubleshooting

### Error: "Celery is not running"
**Solución:**
```powershell
cd backend
celery -A config worker -l info --pool=solo
```

### Error: "Redis connection refused"
**Solución:**
```powershell
cd backend/redis
./redis-server.exe redis.windows.conf
```

### Click en "Iniciar" no hace nada
**Verificar en Console (F12):**
- Si hay error de conexión → Backend no está respondiendo
- Si dice "No hay análisis disponible" → analysisId no se cargó correctamente

### Detecciones no aparecen
**Verificar:**
1. Celery está corriendo (ver terminal de Celery)
2. WebSocket conectado (ver Console: "✅ WebSocket conectado")
3. Video existe en backend/media/traffic_videos/

## 📝 Checklist Final

- [ ] Django corriendo en 8001
- [ ] Redis corriendo en 6379
- [ ] Celery worker corriendo
- [ ] Frontend corriendo en 5174
- [ ] Video cargado en /camera/2
- [ ] Console (F12) abierto para ver logs
- [ ] Click en "Iniciar"
- [ ] Ver detecciones en panel de logs

## 🎯 Resultado Esperado

**Después de click en "Iniciar":**

```
┌─────────────────────────────────────────────┐
│ Panel de Información                        │
├─────────────────────────────────────────────┤
│ UBICACIÓN: Ciudadela Alfonso                │
│ INICIO: 13/10/2025:13:45                   │
│ TIEMPO: 0h0m15s                             │
│ ELMENT. CONTADO: 8                          │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Panel de Logs (Detecciones en Tiempo Real) │
├─────────────────────────────────────────────┤
│ 13:45:23 tipo: auto, placa ABC-1234         │
│ 13:45:25 tipo: camión, placa desconocida    │
│ 13:45:27 tipo: moto, placa XYZ-5678         │
│ 13:45:29 tipo: auto, placa DEF-9876         │
│ 13:45:31 tipo: camioneta, placa GHI-5432    │
│ 13:45:33 tipo: bus, placa desconocida       │
│ 13:45:35 tipo: auto, placa JKL-1357         │
│ 13:45:37 tipo: camión, placa MNO-2468       │
└─────────────────────────────────────────────┘
```

---

**Última actualización:** 13/10/2025 - 04:20 AM
**Estado:** ✅ Frontend listo - ⚠️ Verificar Celery y Redis
