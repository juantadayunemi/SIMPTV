# 🎥 Sistema de Monitoreo en Tiempo Real - Plan de Implementación

## 📋 Descripción General

Sistema de monitoreo de tráfico en tiempo real que permite visualizar hasta **3 videos simultáneos** con detección de vehículos mediante YOLO + Deep SORT, overlay de bounding boxes en canvas, y controles de análisis en vivo.

---

## 🎯 Requisitos Funcionales

### 1. **Lista de Cámaras (CamerasPage)**

#### 1.1 Card de Cámara
Cada card debe mostrar:
- ✅ Video en vivo (si está activa) o placeholder (si está inactiva)
- ✅ Canvas overlay con bounding boxes en tiempo real
- ✅ Indicador de estado: **Activa** (verde), **Inactiva** (rojo), **Mantenimiento** (amarillo)
- ✅ Badge "EN VIVO" cuando está analizando
- ✅ Estadísticas básicas: Velocidad promedio, Vehículos detectados, Congestión %

#### 1.2 Menú de Opciones (3 puntos)
Al hacer click en los 3 puntos, debe aparecer menú con:
- 🔌 **Conectar Video** → Abre modal con 3 opciones:
  - **Path Local** (ej: `C:/videos/traffic_01.mp4`)
  - **URL de Video** (ej: `http://example.com/video.mp4`)
  - **Stream RTSP** (ej: `rtsp://192.168.1.100:554/stream`)
- ⚙️ **Configurar Cámara** → Redirige a `CameraConfigPage`
- ▶️ **Iniciar Análisis** → Inicia reproducción + análisis en la card

#### 1.3 Estados de Cámara

| Estado | Color | Icono | Descripción | Acciones Permitidas |
|--------|-------|-------|-------------|---------------------|
| **Activa** | Verde | `<Wifi />` | Analizando video en tiempo real | Pausar, Ver detalles, Configurar |
| **Inactiva** | Rojo | `<WifiOff />` | Sin video cargado | Conectar video, Configurar |
| **Mantenimiento** | Amarillo | `<Settings />` | En configuración o error | Solo Configurar |

#### 1.4 Límite de Videos Simultáneos
- ⚠️ **Máximo 3 videos simultáneos**
- Si intenta iniciar un 4to video → Mostrar alerta:
  ```
  ⚠️ Memoria insuficiente
  Tu equipo no puede procesar más de 3 videos simultáneamente.
  Detén un análisis antes de iniciar otro.
  ```

#### 1.5 Click en Video
- Si el video está reproduciéndose → Abrir vista ampliada (`VideoDetailPage`)

---

### 2. **Modal de Conexión de Video**

#### 2.1 Componente: `VideoSourceModal.tsx`

**Props:**
```typescript
interface VideoSourceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConnect: (source: VideoSource) => Promise<void>;
  cameraId: number;
}

interface VideoSource {
  type: 'local' | 'url' | 'rtsp';
  value: string;
}
```

**UI:**
```
┌─────────────────────────────────────────────┐
│  Conectar Video                         [X] │
├─────────────────────────────────────────────┤
│                                             │
│  Selecciona el origen del video:           │
│                                             │
│  ⚪ Path Local                              │
│     C:\videos\traffic_01.mp4               │
│     [Explorar...]                           │
│                                             │
│  ⚪ URL de Video                            │
│     http://example.com/video.mp4           │
│                                             │
│  ⚪ Stream RTSP                             │
│     rtsp://192.168.1.100:554/stream        │
│                                             │
├─────────────────────────────────────────────┤
│               [Cancelar]  [Conectar]        │
└─────────────────────────────────────────────┘
```

**Validaciones:**
- Path local: Verificar que sea ruta válida y archivo exista
- URL: Validar formato URL válido
- RTSP: Validar formato `rtsp://...`

**Flujo:**
1. Usuario selecciona tipo (Path/URL/RTSP)
2. Ingresa valor
3. Click "Conectar"
4. Frontend guarda `videoSource` en estado de cámara
5. Cierra modal
6. Usuario puede hacer click en "Iniciar Análisis"

---

### 3. **Mini-Player en Card (Opción 1: Video Local + Canvas Overlay)**

#### 3.1 Componente: `CameraVideoPlayer.tsx`

**Props:**
```typescript
interface CameraVideoPlayerProps {
  cameraId: number;
  videoSource: string; // Blob URL o path
  isActive: boolean;
  onVideoClick: () => void;
}
```

**Estructura HTML:**
```html
<div class="video-container">
  <!-- Video original (reproduce archivo local) -->
  <video 
    id="video-player"
    src={videoBlobUrl}
    autoPlay
    loop
    muted
  />
  
  <!-- Canvas overlay (dibuja bounding boxes) -->
  <canvas 
    id="detection-overlay"
    width={videoWidth}
    height={videoHeight}
  />
</div>
```

**Lógica de Renderizado:**
```typescript
useEffect(() => {
  const video = videoRef.current;
  const canvas = canvasRef.current;
  const ctx = canvas.getContext('2d');
  
  // WebSocket: recibir detecciones en tiempo real
  ws.on('vehicle_detected', (detection) => {
    // Guardar detección con timestamp
    detectionsBuffer.push({
      ...detection,
      timestamp: detection.frame_time // segundos en el video
    });
  });
  
  // Renderizar bounding boxes sincronizados con video.currentTime
  const renderLoop = () => {
    const currentTime = video.currentTime;
    
    // Filtrar detecciones de los últimos 0.5 segundos
    const activeDetections = detectionsBuffer.filter(d => 
      Math.abs(d.timestamp - currentTime) < 0.5
    );
    
    // Limpiar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Dibujar bounding boxes
    activeDetections.forEach(detection => {
      const { bbox, vehicle_type, confidence } = detection;
      
      ctx.strokeStyle = getColorByType(vehicle_type);
      ctx.lineWidth = 3;
      ctx.strokeRect(bbox.x, bbox.y, bbox.width, bbox.height);
      
      // Etiqueta
      ctx.fillStyle = getColorByType(vehicle_type);
      ctx.fillRect(bbox.x, bbox.y - 25, 120, 25);
      ctx.fillStyle = 'white';
      ctx.font = '14px Arial';
      ctx.fillText(`${vehicle_type} ${(confidence * 100).toFixed(0)}%`, bbox.x + 5, bbox.y - 8);
    });
    
    requestAnimationFrame(renderLoop);
  };
  
  renderLoop();
}, [videoSource]);
```

**Colores por Tipo de Vehículo:**
```typescript
const VEHICLE_COLORS = {
  car: '#3B82F6',       // Azul
  truck: '#F59E0B',     // Naranja
  motorcycle: '#10B981', // Verde
  bus: '#8B5CF6',       // Púrpura
  bicycle: '#EC4899'    // Rosa
};
```

---

### 4. **Vista Ampliada (VideoDetailPage)**

#### 4.1 Componente: `VideoDetailPage.tsx`

**URL:** `/traffic/cameras/:cameraId/live`

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  [← Atrás]  Cámara 1 - En Línea                     🔴      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────┐         │
│  │                                               │         │
│  │          VIDEO GRANDE (Canvas Overlay)        │         │
│  │                                               │         │
│  │           [Reconectar] [Pausa] [Iniciar]     │         │
│  └───────────────────────────────────────────────┘         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  LOG DE DETECCIONES          │   ESTADÍSTICAS              │
│  ───────────────────────────────────────────────────────   │
│  14:25:14 auto detectado     │   UBICACIÓN: INSIV-001      │
│  14:25:18 camión detectado   │   INICIO: 05/02/2025:06:02  │
│  14:25:36 auto detectado     │   TIEMPO: 4h2m3s            │
│  14:26:10 bus detectado      │   ELEMENT.CONTADO: 1256     │
│  ...                          │                             │
│                               │   🚗 Cars: 856              │
│                               │   🚚 Trucks: 234            │
│                               │   🏍️ Motorcycles: 145       │
│                               │   🚌 Buses: 21              │
└─────────────────────────────────────────────────────────────┘
```

#### 4.2 Controles

**Botón "Reconectar":**
- Abre `VideoSourceModal` para seleccionar nuevo path
- Al conectar:
  1. Detiene análisis actual (si estaba corriendo)
  2. Limpia buffer de detecciones
  3. Envía nuevo video al backend (chunked upload)
  4. Muestra mensaje: "📤 Analizando... espera ~5 segundos"
  5. Backend procesa primeros chunks y empieza a enviar datos
  6. Video comienza a reproducirse con overlay

**Botón "Pausa":**
- Pausa reproducción del video (frontend)
- Envía señal al backend: `POST /api/traffic/analyses/:id/pause/`
- Backend detiene procesamiento de frames temporalmente
- Botón cambia a "Reanudar"

**Botón "Iniciar":**
- Solo visible si video está pausado o no hay video
- Reanuda reproducción + análisis

**Botón "Atrás":**
- Regresa a `CamerasPage`
- **NO detiene el análisis** (sigue corriendo en background)
- En la lista, la card muestra el video en mini-player

#### 4.3 Log de Detecciones
- Auto-scroll al final cuando llegan nuevas detecciones
- Formato: `[HH:MM:SS] {tipo_vehiculo} detectado, placa {placa}`
- Máximo 200 líneas en memoria (FIFO)

#### 4.4 Panel de Estadísticas
- **Ubicación**: Nombre de la ubicación de la cámara
- **Inicio**: Fecha/hora de inicio del análisis
- **Tiempo**: Duración del análisis en formato `Xh Ym Zs`
- **Elementos Contados**: Total de vehículos únicos detectados
- **Contadores por Tipo**: Cars, Trucks, Motorcycles, Buses

---

### 5. **Configuración de Cámara (CameraConfigPage)**

#### 5.1 Renombrar Archivo
```
❌ TrafficAnalysisPage.tsx
✅ CameraConfigPage.tsx
```

**Nueva URL:** `/traffic/cameras/:cameraId/config`

#### 5.2 Secciones

**A. Información General**
```
┌─────────────────────────────────────────────┐
│  Información de la Cámara                   │
├─────────────────────────────────────────────┤
│  Nombre:       [Cámara Norte           ]    │
│  Marca:        [Hikvision              ]    │
│  Modelo:       [DS-2CD2385G1          ]    │
│  Resolución:   [1920x1080             ]    │
│  FPS:          [30                     ]    │
│  Carriles:     [2                      ]    │
│  Bidireccional: ☑️                          │
└─────────────────────────────────────────────┘
```

**B. Ubicación (CON MEJORAS)**
```
┌─────────────────────────────────────────────┐
│  Ubicación                                  │
├─────────────────────────────────────────────┤
│  Ubicación Actual:                          │
│  📍 Av. Principal - Intersección Norte      │
│                                             │
│  [Cambiar Ubicación ▼]                     │
│  ┌─────────────────────────────────────┐   │
│  │ • Av. Principal - Intersección Norte│   │
│  │ • Av. Secundaria - Cruce Central    │   │
│  │ • Puente Norte - Salida A1          │   │
│  │ ➕ Buscar por Mapa                  │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**Flujo "Buscar por Mapa":**
1. Click en "➕ Buscar por Mapa"
2. Abre modal con mapa interactivo (Google Maps / Leaflet)
3. Usuario hace click en el mapa
4. Sistema obtiene coordenadas (lat, lng)
5. Reverse geocoding para obtener dirección
6. Crea nueva ubicación automáticamente
7. Asigna ubicación a la cámara

**C. Estado de Mantenimiento**
```
┌─────────────────────────────────────────────┐
│  Estado                                     │
├─────────────────────────────────────────────┤
│  ⚪ Activa (permite análisis de video)      │
│  ⚪ Inactiva (cámara deshabilitada)         │
│  ⚪ Mantenimiento (solo configuración)      │
│                                             │
│  ℹ️ En modo Mantenimiento no se pueden      │
│     iniciar análisis. Solo configuración.   │
└─────────────────────────────────────────────┘
```

**Lógica de Estados:**
- **Activa**: Usuario puede iniciar análisis (subir videos)
- **Inactiva**: Cámara deshabilitada, no aparece en lista principal
- **Mantenimiento**: Aparece en lista pero con funciones bloqueadas
  - ❌ No se puede hacer click en "Conectar Video"
  - ❌ No se puede hacer click en "Iniciar Análisis"
  - ✅ SÍ se puede hacer click en "Configurar Cámara"

**Transiciones Automáticas:**
- Si ocurre un error durante análisis → Estado cambia a **Mantenimiento**
- Usuario debe revisar configuración y habilitar manualmente

---

## 🏗️ Arquitectura Técnica

### 6. Backend - Nuevos Endpoints

#### 6.1 Endpoints de Análisis

**A. Pausar Análisis**
```http
POST /api/traffic/analyses/:id/pause/

Response:
{
  "status": "paused",
  "message": "Análisis pausado exitosamente"
}
```

**Backend:**
```python
# apps/traffic_app/views.py
@action(detail=True, methods=['post'])
def pause(self, request, pk=None):
    analysis = self.get_object()
    
    # Enviar señal a Celery task para pausar
    analysis.status = 'PAUSED'
    analysis.save()
    
    # WebSocket: notificar al frontend
    send_websocket_event(analysis.id, {
        'type': 'analysis_paused',
        'data': {'message': 'Análisis pausado'}
    })
    
    return Response({'status': 'paused'})
```

**B. Reanudar Análisis**
```http
POST /api/traffic/analyses/:id/resume/

Response:
{
  "status": "processing",
  "message": "Análisis reanudado"
}
```

**C. Detener Análisis**
```http
POST /api/traffic/analyses/:id/stop/

Response:
{
  "status": "stopped",
  "message": "Análisis detenido y finalizado"
}
```

**D. Reconectar Video**
```http
POST /api/traffic/analyses/:id/reconnect/

Body:
{
  "videoSource": {
    "type": "local",
    "value": "C:/videos/traffic_02.mp4"
  }
}

Response:
{
  "status": "reconnecting",
  "message": "Iniciando análisis con nuevo video"
}
```

**Backend:**
```python
@action(detail=True, methods=['post'])
def reconnect(self, request, pk=None):
    analysis = self.get_object()
    video_source = request.data.get('videoSource')
    
    # Detener análisis actual
    analysis.status = 'STOPPED'
    analysis.save()
    
    # Crear nuevo análisis con mismo cameraId
    new_analysis = TrafficAnalysis.objects.create(
        cameraId=analysis.cameraId,
        locationId=analysis.locationId,
        videoPath=video_source['value'],
        status='PENDING'
    )
    
    # Iniciar tarea Celery
    process_video_analysis.delay(new_analysis.id)
    
    return Response({
        'status': 'reconnecting',
        'analysisId': new_analysis.id
    })
```

#### 6.2 Endpoints de Cámara

**A. Actualizar Estado**
```http
PATCH /api/traffic/cameras/:id/

Body:
{
  "status": "maintenance" | "active" | "inactive"
}

Response:
{
  "id": 1,
  "name": "Cámara Norte",
  "status": "maintenance"
}
```

**B. Actualizar Ubicación**
```http
PATCH /api/traffic/cameras/:id/

Body:
{
  "locationId": 5
}

Response:
{
  "id": 1,
  "name": "Cámara Norte",
  "locationId": 5,
  "locationName": "Puente Norte - Salida A1"
}
```

**C. Obtener Cámaras Activas**
```http
GET /api/traffic/cameras/active/

Response:
{
  "count": 3,
  "cameras": [
    {
      "id": 1,
      "name": "Cámara Norte",
      "status": "active",
      "currentAnalysisId": 45
    }
  ]
}
```

#### 6.3 WebSocket - Nuevos Eventos

**A. Análisis Pausado**
```json
{
  "type": "analysis_paused",
  "data": {
    "analysisId": 123,
    "pausedAt": "2025-10-10T14:30:00Z"
  }
}
```

**B. Análisis Reanudado**
```json
{
  "type": "analysis_resumed",
  "data": {
    "analysisId": 123,
    "resumedAt": "2025-10-10T14:35:00Z"
  }
}
```

**C. Error de Análisis (Auto-mantenimiento)**
```json
{
  "type": "analysis_error",
  "data": {
    "analysisId": 123,
    "cameraId": 1,
    "error": "Video file corrupted",
    "cameraStatus": "maintenance"
  }
}
```

---

### 7. Frontend - Nuevos Componentes

#### 7.1 Estructura de Archivos
```
frontend/src/
├── components/
│   └── traffic/
│       ├── CameraVideoPlayer.tsx        # ✨ NUEVO - Mini-player con canvas
│       ├── VideoSourceModal.tsx         # ✨ NUEVO - Modal de conexión
│       ├── VideoDetailView.tsx          # ✨ NUEVO - Vista ampliada
│       ├── AnalysisControls.tsx         # ✨ NUEVO - Controles (Pausa/Reconectar)
│       ├── DetectionLog.tsx             # ✨ NUEVO - Log auto-scroll
│       ├── LiveStats.tsx                # ✨ NUEVO - Estadísticas en tiempo real
│       └── LocationSelector.tsx         # ✨ NUEVO - Selector de ubicación
│
├── pages/
│   └── traffic/
│       ├── CamerasPage.tsx              # 🔄 ACTUALIZAR
│       ├── VideoDetailPage.tsx          # ✨ NUEVO
│       └── CameraConfigPage.tsx         # 🔄 RENOMBRAR + ACTUALIZAR
│
├── services/
│   ├── traffic.service.ts               # 🔄 ACTUALIZAR - Agregar métodos pause/resume/stop
│   └── websocket.service.ts             # 🔄 ACTUALIZAR - Agregar eventos nuevos
│
└── hooks/
    ├── useVideoAnalysis.ts              # ✨ NUEVO - Lógica de análisis
    └── useActiveAnalyses.ts             # ✨ NUEVO - Contador de videos simultáneos
```

#### 7.2 Hook: `useActiveAnalyses.ts`
```typescript
import { useState, useEffect } from 'react';
import { trafficService } from '@/services/traffic.service';

export const useActiveAnalyses = () => {
  const [activeCount, setActiveCount] = useState(0);
  const [activeAnalyses, setActiveAnalyses] = useState<number[]>([]);
  
  const MAX_SIMULTANEOUS = 3;
  
  const canStartNew = activeCount < MAX_SIMULTANEOUS;
  
  const startAnalysis = async (cameraId: number, videoSource: VideoSource) => {
    if (!canStartNew) {
      throw new Error('Memoria insuficiente. Tu equipo no puede procesar más de 3 videos simultáneamente.');
    }
    
    const analysis = await trafficService.startAnalysis(cameraId, videoSource);
    setActiveAnalyses(prev => [...prev, analysis.id]);
    setActiveCount(prev => prev + 1);
    
    return analysis;
  };
  
  const stopAnalysis = async (analysisId: number) => {
    await trafficService.stopAnalysis(analysisId);
    setActiveAnalyses(prev => prev.filter(id => id !== analysisId));
    setActiveCount(prev => prev - 1);
  };
  
  useEffect(() => {
    // Cargar análisis activos al montar
    const loadActive = async () => {
      const cameras = await trafficService.getActiveCameras();
      const activeIds = cameras
        .filter(c => c.currentAnalysisId)
        .map(c => c.currentAnalysisId!);
      
      setActiveAnalyses(activeIds);
      setActiveCount(activeIds.length);
    };
    
    loadActive();
  }, []);
  
  return {
    activeCount,
    canStartNew,
    startAnalysis,
    stopAnalysis,
    MAX_SIMULTANEOUS
  };
};
```

#### 7.3 Hook: `useVideoAnalysis.ts`
```typescript
import { useState, useEffect, useRef } from 'react';
import { getWebSocketService } from '@/services/websocket.service';

interface Detection {
  track_id: number;
  vehicle_type: string;
  bbox: { x: number; y: number; width: number; height: number };
  confidence: number;
  timestamp: number;
}

export const useVideoAnalysis = (analysisId: number | null) => {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const wsRef = useRef<any>(null);
  
  useEffect(() => {
    if (!analysisId) return;
    
    const ws = getWebSocketService();
    wsRef.current = ws;
    
    ws.connect(analysisId);
    
    ws.on('vehicle_detected', (data: Detection) => {
      setDetections(prev => [...prev, data].slice(-50)); // Keep last 50
      
      const logEntry = `[${new Date().toLocaleTimeString()}] ${data.vehicle_type} detectado`;
      setLogs(prev => [...prev, logEntry].slice(-200)); // Keep last 200
    });
    
    ws.on('stats_update', (data: any) => {
      setStats(data);
    });
    
    return () => {
      ws.disconnect();
    };
  }, [analysisId]);
  
  return {
    detections,
    stats,
    logs,
    ws: wsRef.current
  };
};
```

---

## 📝 Checklist de Implementación

### Fase 1: Backend - Control de Análisis ✅
- [ ] Endpoint: `POST /api/traffic/analyses/:id/pause/`
- [ ] Endpoint: `POST /api/traffic/analyses/:id/resume/`
- [ ] Endpoint: `POST /api/traffic/analyses/:id/stop/`
- [ ] Endpoint: `POST /api/traffic/analyses/:id/reconnect/`
- [ ] Endpoint: `GET /api/traffic/cameras/active/`
- [ ] Endpoint: `PATCH /api/traffic/cameras/:id/` (actualizar estado)
- [ ] WebSocket: Eventos `analysis_paused`, `analysis_resumed`, `analysis_error`
- [ ] Celery Task: Lógica de pausa/reanudación

### Fase 2: Backend - Estados de Cámara ✅
- [ ] Modelo: Agregar campo `status` a Camera (active/inactive/maintenance)
- [ ] Migration: `python manage.py makemigrations`
- [ ] Lógica: Transición automática a "maintenance" en errores
- [ ] Validación: Bloquear inicio de análisis si status != "active"

### Fase 3: Frontend - Componentes Base ✅
- [ ] Componente: `VideoSourceModal.tsx`
- [ ] Componente: `CameraVideoPlayer.tsx` (video + canvas overlay)
- [ ] Componente: `AnalysisControls.tsx` (Pausa/Reconectar/Iniciar)
- [ ] Componente: `DetectionLog.tsx` (auto-scroll)
- [ ] Componente: `LiveStats.tsx`
- [ ] Componente: `LocationSelector.tsx` (lista + mapa)

### Fase 4: Frontend - Páginas ✅
- [ ] Actualizar: `CamerasPage.tsx`
  - [ ] Agregar menú de 3 puntos
  - [ ] Integrar `CameraVideoPlayer` en cards
  - [ ] Mostrar badge "EN VIVO"
  - [ ] Click en video → Navegar a `VideoDetailPage`
- [ ] Crear: `VideoDetailPage.tsx`
  - [ ] Layout grande
  - [ ] Integrar `AnalysisControls`
  - [ ] Integrar `DetectionLog`
  - [ ] Integrar `LiveStats`
  - [ ] Botón "Atrás"
- [ ] Renombrar: `TrafficAnalysisPage.tsx` → `CameraConfigPage.tsx`
  - [ ] Sección: Información General
  - [ ] Sección: Ubicación (con mapa)
  - [ ] Sección: Estado de Mantenimiento

### Fase 5: Frontend - Servicios ✅
- [ ] Actualizar: `traffic.service.ts`
  - [ ] Método: `pauseAnalysis(id)`
  - [ ] Método: `resumeAnalysis(id)`
  - [ ] Método: `stopAnalysis(id)`
  - [ ] Método: `reconnectAnalysis(id, videoSource)`
  - [ ] Método: `getActiveCameras()`
  - [ ] Método: `updateCameraStatus(id, status)`
- [ ] Actualizar: `websocket.service.ts`
  - [ ] Handler: `analysis_paused`
  - [ ] Handler: `analysis_resumed`
  - [ ] Handler: `analysis_error`

### Fase 6: Frontend - Hooks ✅
- [ ] Hook: `useActiveAnalyses.ts`
  - [ ] Contador de análisis activos
  - [ ] Validación de máximo 3 simultáneos
  - [ ] Método: `startAnalysis()`
  - [ ] Método: `stopAnalysis()`
- [ ] Hook: `useVideoAnalysis.ts`
  - [ ] Buffer de detecciones (últimas 50)
  - [ ] Buffer de logs (últimos 200)
  - [ ] Estadísticas en tiempo real

### Fase 7: Testing ✅
- [ ] Test: Iniciar 3 videos simultáneos → OK
- [ ] Test: Intentar iniciar 4to video → Mostrar alerta
- [ ] Test: Pausar análisis → Video se pausa + backend detiene procesamiento
- [ ] Test: Reconectar video → Nuevo video se carga y analiza
- [ ] Test: Cambiar estado a "Mantenimiento" → Funciones bloqueadas
- [ ] Test: Error en análisis → Estado cambia automáticamente a "Mantenimiento"
- [ ] Test: Canvas overlay sincronizado con video.currentTime

---

## 🎨 Mockups de Referencia

### Lista de Cámaras
```
┌─────────────────────────────────────────────────────────────┐
│  Gestión de Cámaras                    [Todas ▼] [+ Agregar] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐         │
│  │ [⋮]            🔴    │  │ [⋮]            🔴    │         │
│  │ ┌───────────────┐   │  │ ┌───────────────┐   │         │
│  │ │   VIDEO CON   │   │  │ │   VIDEO CON   │   │         │
│  │ │  BOUNDING BOX │   │  │ │  BOUNDING BOX │   │         │
│  │ └───────────────┘   │  │ └───────────────┘   │         │
│  │ Cámara Norte        │  │ Cámara Sur         │         │
│  │ 📍 Intersección     │  │ 📍 Av. Principal   │         │
│  │ ✅ Activa           │  │ ✅ Activa          │         │
│  │ 🚗 12 vehículos     │  │ 🚗 8 vehículos     │         │
│  └─────────────────────┘  └─────────────────────┘         │
│                                                             │
│  ┌─────────────────────┐                                   │
│  │ [⋮]                 │                                   │
│  │ ┌───────────────┐   │                                   │
│  │ │   NO HAY      │   │                                   │
│  │ │   VIDEO       │   │                                   │
│  │ └───────────────┘   │                                   │
│  │ Cámara Este         │                                   │
│  │ 📍 Puente A1        │                                   │
│  │ ⚙️ Mantenimiento    │                                   │
│  └─────────────────────┘                                   │
└─────────────────────────────────────────────────────────────┘
```

### Menú de 3 Puntos
```
┌─────────────────────────┐
│ 🔌 Conectar Video       │
│ ⚙️ Configurar Cámara    │
│ ▶️ Iniciar Análisis     │
└─────────────────────────┘
```

### Vista Ampliada
```
┌─────────────────────────────────────────────────────────────┐
│  [← Atrás]  Cámara 1 - En Línea                     🔴      │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐ │
│  │                                                       │ │
│  │              VIDEO GRANDE (1280x720)                 │ │
│  │           con Canvas Overlay (Bounding Boxes)        │ │
│  │                                                       │ │
│  │        [Reconectar]  [⏸ Pausa]  [▶ Iniciar]         │ │
│  └───────────────────────────────────────────────────────┘ │
├────────────────────────────────┬────────────────────────────┤
│  LOG DE DETECCIONES            │   ESTADÍSTICAS             │
│  ────────────────────────────  │  ─────────────────────     │
│  [14:25:14] auto detectado     │  📍 UBICACIÓN: INSIV-001   │
│  [14:25:18] camión detectado   │  🕐 INICIO: 05/02 06:02    │
│  [14:25:36] auto detectado     │  ⏱️ TIEMPO: 4h2m3s         │
│  [14:26:10] bus detectado      │  🎯 CONTADOS: 1256         │
│  [14:26:25] moto detectada     │                            │
│  ...                            │  🚗 Cars: 856              │
│                                 │  🚚 Trucks: 234            │
│                                 │  🏍️ Motorcycles: 145       │
│                                 │  🚌 Buses: 21              │
└────────────────────────────────┴────────────────────────────┘
```

---

## 🚀 Orden de Implementación Recomendado

### Sesión 1: Backend Control de Análisis (2-3 horas)
1. Endpoints: pause, resume, stop, reconnect
2. WebSocket: Eventos nuevos
3. Celery: Lógica de pausa/reanudación

### Sesión 2: Backend Estados de Cámara (1-2 horas)
1. Modelo: Campo `status`
2. Migration
3. Lógica de transiciones automáticas

### Sesión 3: Frontend Componentes Base (3-4 horas)
1. `VideoSourceModal.tsx`
2. `CameraVideoPlayer.tsx` (video + canvas)
3. `AnalysisControls.tsx`

### Sesión 4: Frontend Páginas (3-4 horas)
1. Actualizar `CamerasPage.tsx`
2. Crear `VideoDetailPage.tsx`
3. Renombrar y actualizar `CameraConfigPage.tsx`

### Sesión 5: Frontend Servicios + Hooks (2-3 horas)
1. Actualizar `traffic.service.ts`
2. Actualizar `websocket.service.ts`
3. Crear `useActiveAnalyses.ts`
4. Crear `useVideoAnalysis.ts`

### Sesión 6: Testing e Integración (2-3 horas)
1. Pruebas de límite de 3 videos
2. Pruebas de pausa/reconexión
3. Pruebas de sincronización canvas
4. Ajustes finales de UI/UX

**Total Estimado: 13-19 horas de desarrollo**

---

## 📚 Documentos Relacionados

- `VIDEO_PROCESSING_SYSTEM.md` - Sistema de procesamiento de video base
- `ARQUITECTURA_DLL.md` - Sincronización TypeScript ↔ Django
- `IMPLEMENTATION_PLAN.md` - Plan general del proyecto

---

✅ **Plan de trabajo guardado exitosamente!**

🎯 **Próximo paso:** Crear nueva app en backend para que otro desarrollador trabaje.

