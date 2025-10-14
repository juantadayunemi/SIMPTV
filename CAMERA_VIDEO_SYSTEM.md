# 🎥 Sistema de Video por Cámara - Documentación

## 📋 Concepto

Cada cámara tiene **UN video asignado** que se usa para el análisis. Cuando subes un video a una cámara, ese video queda **asociado permanentemente** a esa cámara hasta que subas otro.

## 🗄️ Modelo de Datos

### Camera (Cámara)
```python
class Camera:
    id: int
    name: str
    locationId: ForeignKey(Location)
    
    # 🆕 CAMPOS NUEVOS:
    currentVideoPath: str (opcional)      # Ruta del video asignado
    currentAnalysisId: ForeignKey(TrafficAnalysis)  # Análisis activo
```

### TrafficAnalysis (Análisis de Tráfico)
```python
class TrafficAnalysis:
    id: int
    cameraId: ForeignKey(Camera)    # Cámara que hizo el análisis
    videoPath: str                  # Video usado en este análisis
    status: str                     # PENDING, PROCESSING, COMPLETED
    # ... estadísticas ...
```

## 🔄 Flujo de Trabajo

### 1. Subir Video a una Cámara

```
Usuario → Cámaras → Click "Reproducir" → Subir Video
```

**Backend (`/api/traffic/analyze-video/`):**
```python
# 1. Guardar video
video_path = save_video(file)

# 2. Crear análisis
analysis = TrafficAnalysis.create(
    cameraId=camera_id,
    videoPath=video_path,
    status='PENDING'
)

# 3. 🆕 ACTUALIZAR CÁMARA
camera.currentVideoPath = video_path
camera.currentAnalysisId = analysis.id
camera.status = 'ACTIVE'
camera.save()
```

**Resultado:**
- ✅ Video guardado en: `media/traffic_videos/YYYYMMDD_HHMMSS_filename.mp4`
- ✅ Análisis creado con estado PENDING
- ✅ Cámara actualizada con el video y análisis

### 2. Reproducir Video de una Cámara

```
Usuario → /camera/:id
```

**Frontend (`CameraLiveAnalysisPage.tsx`):**
```typescript
// 1. Obtener analysisId del state (viene de navegación)
const analysisId = locationState?.analysisId;

// 2. Cargar análisis
const analysis = await trafficService.getAnalysis(analysisId);

// 3. Obtener videoPath del análisis
const videoUrl = `${API_URL}/media/${analysis.videoPath}`;

// 4. Cargar video en el player
<video src={videoUrl} />
```

**Resultado:**
- ✅ Video se carga en el reproductor
- ✅ Video corresponde a la cámara seleccionada
- ✅ No se mezclan videos entre cámaras

### 3. Iniciar Análisis

```
Usuario → Click "Iniciar"
```

**Frontend:**
```typescript
const result = await trafficService.startAnalysis(analysisId);
```

**Backend (`/api/traffic/analysis/:id/start/`):**
```python
# 1. Obtener análisis
analysis = TrafficAnalysis.objects.get(id=analysisId)

# 2. Obtener video_path
video_path = analysis.videoPath

# 3. Iniciar procesamiento con YOLOv8 + EasyOCR
task = process_video_analysis.delay(
    analysis_id=analysisId,
    video_path=video_path
)

# 4. Actualizar estado
analysis.status = 'PROCESSING'
analysis.isPlaying = True
analysis.isPaused = False
analysis.save()
```

**Resultado:**
- ✅ Celery procesa el video de esa cámara específica
- ✅ WebSocket envía detecciones en tiempo real
- ✅ Frontend muestra logs de detección

## 🔐 Garantías del Sistema

### 1. **Aislamiento de Videos por Cámara**
- ❌ **NO PUEDE:** Cámara A usar video de Cámara B
- ✅ **SÍ PUEDE:** Cámara A tener múltiples análisis históricos de su propio video

### 2. **Relación Cámara-Video**
```
Camera
  └── currentVideoPath: "traffic_videos/20251013_142530_highway.mp4"
  └── currentAnalysisId: 5
      └── TrafficAnalysis (id=5)
          └── videoPath: "traffic_videos/20251013_142530_highway.mp4"
          └── cameraId: 1
```

### 3. **Historial de Análisis**
Una cámara puede tener varios análisis del mismo video:
```
Camera (id=1) → currentVideoPath: "highway.mp4"
  ├── TrafficAnalysis (id=5) → videoPath: "highway.mp4" [COMPLETED]
  ├── TrafficAnalysis (id=8) → videoPath: "highway.mp4" [COMPLETED]
  └── TrafficAnalysis (id=12) → videoPath: "highway.mp4" [PROCESSING] ← Activo
```

## 📊 Endpoints API

### Subir Video
```http
POST /api/traffic/analyze-video/
Content-Type: multipart/form-data

video: File
cameraId: 1
```

**Response:**
```json
{
  "id": 5,
  "message": "Video uploaded and analysis started successfully",
  "task_id": "celery-task-uuid",
  "status": "PROCESSING"
}
```

### Obtener Análisis
```http
GET /api/traffic/analysis/:id/
```

**Response:**
```json
{
  "id": 5,
  "cameraId": 1,
  "videoPath": "traffic_videos/20251013_142530_highway.mp4",
  "status": "PROCESSING",
  "totalVehicleCount": 45,
  ...
}
```

### Iniciar Análisis
```http
POST /api/traffic/analysis/:id/start/
```

**Response:**
```json
{
  "message": "Analysis started successfully",
  "analysis_id": 5,
  "task_id": "celery-task-uuid",
  "status": "PROCESSING",
  "isPlaying": true,
  "isPaused": false
}
```

## 🎯 Casos de Uso

### Caso 1: Nueva Cámara, Primer Video
```
1. Usuario sube video a Cámara A
2. Camera.currentVideoPath = "video1.mp4"
3. Camera.currentAnalysisId = 1
4. TrafficAnalysis (id=1) creado
5. Usuario puede iniciar análisis
```

### Caso 2: Cambiar Video de una Cámara
```
1. Usuario sube nuevo video a Cámara A
2. Camera.currentVideoPath = "video2.mp4" (sobrescribe)
3. Camera.currentAnalysisId = 5 (nuevo análisis)
4. TrafficAnalysis (id=5) creado
5. Análisis anterior (id=1) sigue existiendo con "video1.mp4"
```

### Caso 3: Múltiples Análisis del Mismo Video
```
1. Cámara A tiene video1.mp4 asignado
2. Usuario hace Análisis 1 → Completa
3. Usuario hace Análisis 2 → Completa
4. Usuario hace Análisis 3 → En proceso
5. Todos usan el mismo video1.mp4
```

## ⚠️ Importante

### ✅ **Hacer:**
- Subir video antes de hacer análisis
- Verificar que `camera.currentVideoPath` existe antes de iniciar análisis
- Usar `analysis.videoPath` para obtener la ruta del video

### ❌ **No Hacer:**
- Iniciar análisis sin haber subido video
- Compartir videos entre cámaras diferentes
- Modificar `videoPath` manualmente en la base de datos

## 🔍 Verificación

### Comprobar que una cámara tiene video:
```python
camera = Camera.objects.get(id=1)
if camera.currentVideoPath:
    print(f"✅ Cámara tiene video: {camera.currentVideoPath}")
else:
    print("❌ Cámara no tiene video asignado")
```

### Comprobar análisis activo:
```python
camera = Camera.objects.get(id=1)
if camera.currentAnalysisId:
    analysis = camera.currentAnalysisId
    print(f"✅ Análisis activo: {analysis.id}, Estado: {analysis.status}")
else:
    print("❌ No hay análisis activo")
```

## 📈 Migración Aplicada

```python
# Migration: 0003_camera_currentanalysisid_camera_currentvideopath.py
operations = [
    migrations.AddField(
        model_name='camera',
        name='currentAnalysisId',
        field=models.ForeignKey(
            blank=True, null=True,
            on_delete=django.db.models.deletion.SET_NULL,
            related_name='active_camera',
            to='traffic_app.trafficanalysis'
        ),
    ),
    migrations.AddField(
        model_name='camera',
        name='currentVideoPath',
        field=models.CharField(
            blank=True, max_length=500, null=True
        ),
    ),
]
```

## ✅ Estado Actual

- ✅ Modelos actualizados (Camera, TrafficAnalysis)
- ✅ Migraciones aplicadas a SQL Server
- ✅ Entidades TypeScript actualizadas
- ✅ Backend actualiza cámara al subir video
- ✅ Frontend carga video desde análisis
- ✅ Sistema listo para pruebas

¡Ahora cada cámara tiene su propio video asignado! 🎉
