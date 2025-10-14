# 🧪 Script de Diagnóstico - Sistema de Video por Cámara

## ✅ Pasos Completados
- [x] Shared: Campos agregados a CameraEntity
- [x] Backend: Modelo Camera actualizado
- [x] Base de Datos: Migración aplicada
- [x] Frontend: Lógica de carga mejorada

## 🔍 Diagnóstico

### 1. Verificar Servidor Backend
```powershell
# Terminal 1: Verificar que Django esté corriendo
curl http://localhost:8001/api/traffic/cameras/
```

### 2. Probar Upload de Video

#### A. Abrir DevTools (F12)
- Ir a: `http://localhost:5175/traffic`
- Click en "▶️ Reproducir" en una cámara
- **Console Tab:** Ver logs

#### B. Ver Logs Esperados en Console:
```javascript
📤 Subiendo video para cámara: 1
📦 FormData contenido: {
  video: "Traffic Flow In The Highway - 4K.mp4",
  size: 24824832,
  type: "video/mp4",
  cameraId: 1
}
```

#### C. Si hay error, verá:
```javascript
❌ Error subiendo video: Error {...}
❌ Error response: { error: "..." }
❌ Error status: 400 / 500
```

### 3. Verificar en Backend (Terminal Django)

Buscar estos logs después de intentar subir:
```
====================================================
📥 ANALYZE VIDEO ENDPOINT
FILES: ['video']
DATA: {'cameraId': '1'}
====================================================
✅ Video file: Traffic...mp4 (24824832 bytes)
📷 Camera ID: 1, Location ID: None
✅ Video guardado: traffic_videos/20251013_...mp4
✅ TrafficAnalysis creado: ID=6
✅ Cámara actualizada: ID=1, Video=..., Analysis=6
✅ Celery task iniciado: ...
```

### 4. Verificar Base de Datos

```sql
-- Ver cámaras y sus videos
SELECT 
    id,
    name,
    currentVideoPath,
    currentAnalysisId,
    status
FROM traffic_cameras;

-- Ver análisis creados
SELECT 
    id,
    cameraId_id,
    videoPath,
    status,
    startedAt
FROM traffic_analysis
ORDER BY id DESC
LIMIT 5;
```

### 5. Verificar Redirección y Carga de Video

#### A. Después de subir video:
- Debería redirigir a: `/camera/1`
- URL en navegador: `http://localhost:5175/camera/1`

#### B. Ver panel azul en la página:
```
┌─────────────────────────────────────┐
│ Análisis ID: 6                      │
│ Video URL: http://localhost:8001/...│
│ ✅ WebSocket conectado              │
└─────────────────────────────────────┘
```

#### C. Ver en Console:
```javascript
📥 Cargando análisis: 6
🎥 Video URL: http://localhost:8001/media/traffic_videos/...mp4
✅ Video cargado correctamente
```

### 6. Verificar Video en Reproductor

#### A. Si el video se carga:
- ✅ Debería verse el player con video
- ✅ Controles visibles
- ✅ Puede reproducir manualmente

#### B. Si NO se carga:
1. Copiar la **Video URL** del panel azul
2. Pegarla en nueva pestaña del navegador
3. Debería descargar/mostrar el video directamente

#### C. Si da 404:
```
Problema: El archivo no existe en el servidor
Solución: Verificar carpeta backend/media/traffic_videos/
```

## 🐛 Troubleshooting

### Error: "Error subiendo el video"

**Revisar Console (F12):**
```javascript
❌ Error response: { error: "mensaje específico" }
```

**Causas comunes:**
1. Backend no está corriendo → Verificar terminal Django
2. Campo faltante → Verificar que se envía 'video' y 'cameraId'
3. Permisos → Verificar carpeta media/ tiene permisos escritura

### Error: Video no aparece después de subir

**Revisar Console (F12):**
```javascript
// Debería ver:
📥 Cargando análisis: X
🎥 Video URL: http://...
```

**Si no ve logs:**
1. analysisId no llegó correctamente
2. Verificar que CamerasPage pasa analysisId en navigate()

**Si ve logs pero no carga video:**
1. Copiar Video URL y abrirla en nueva pestaña
2. Si da 404: El video no existe en el servidor
3. Si descarga: Problema con el reproductor

### Error: Video existe pero no reproduce

**Verificar:**
1. Formato del video (MP4 es más compatible)
2. Codec del video (H.264 es más compatible)
3. Console del navegador: errores de CORS o MIME type

## 🎯 Flujo Exitoso Esperado

```
1. Upload Video
   → FormData enviado con video + cameraId
   → Backend responde: { id: 6, message: "..." }
   
2. Backend Actualiza
   → Camera.currentVideoPath = "traffic_videos/..."
   → Camera.currentAnalysisId = 6
   
3. Frontend Redirige
   → /camera/1 (con state.analysisId = 6)
   
4. Página Carga
   → GET /api/traffic/analysis/6/
   → Obtiene videoPath
   → Construye URL: /media/traffic_videos/...
   
5. Video se Muestra
   → <video> recibe src
   → onLoadedMetadata se dispara
   → Video listo para reproducir
```

## 📝 Checklist de Verificación

- [ ] Backend corriendo en 8001
- [ ] Frontend corriendo en 5175
- [ ] Carpeta media/traffic_videos/ existe
- [ ] DevTools (F12) abierto en Console tab
- [ ] Network tab abierto para ver requests
- [ ] Terminal Django visible para ver logs

## 🚀 Próximos Pasos

Una vez que el video cargue correctamente:
1. Click en "▶️ Iniciar"
2. Verificar que inicia análisis
3. Ver detecciones en tiempo real
4. Confirmar que usa el video correcto

---

**Última actualización:** 13/10/2025
**Estado:** Listo para pruebas
