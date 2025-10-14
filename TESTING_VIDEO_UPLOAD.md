# 🎥 Guía de Prueba: Sistema de Análisis de Video con OCR

## ✅ Configuración Completada

### Backend
- ✅ Carpeta `media/traffic_videos/` creada
- ✅ `.gitignore` actualizado para excluir videos
- ✅ Servidor Django corriendo en `http://localhost:8001`
- ✅ Endpoints de video upload funcionando
- ✅ WebSocket configurado para tiempo real
- ✅ EasyOCR integrado para detección de placas

### Frontend
- ✅ Servidor Vite corriendo en `http://localhost:5175`
- ✅ ConnectPathModal actualizado con cameraId
- ✅ CameraLiveAnalysisPage con carga de video desde análisis
- ✅ DetectionLogPanel para logs en tiempo real
- ✅ WebSocket integrado para recibir detecciones

## 🧪 Pasos para Probar

### 1. Verificar Servidores
```powershell
# Backend (debe estar en puerto 8001)
http://localhost:8001/api/traffic/cameras/

# Frontend (debe estar en puerto 5175)
http://localhost:5175
```

### 2. Flujo Completo de Prueba

#### Paso 1: Ir a Gestión de Cámaras
```
URL: http://localhost:5175/traffic
```

#### Paso 2: Seleccionar una Cámara
- Buscar la cámara **"Ciudadela Alfonso Oramas Gonzalez"**
- Click en el botón **"▶️ Reproducir"**

#### Paso 3: Subir Video
1. Se abre modal "Conectar Video"
2. Arrastrar o seleccionar video de tráfico
3. Archivo recomendado: `Traffic Flow In The Highway - 4K.mp4`
4. Click en **"Reproducir"** (botón azul)

#### Paso 4: Verificar Carga
Deberías ver:
- ✅ Modal mostrando "Subiendo video al backend... 100%"
- ✅ Redirección automática a `/camera/1`
- ✅ Panel azul con:
  - **Análisis ID:** (número)
  - **Video URL:** `http://localhost:8001/media/traffic_videos/...`
  - **Estado WebSocket:** ✅ WebSocket conectado

#### Paso 5: Verificar Video
- ✅ Video debe cargarse en el reproductor
- ✅ Controles de video visibles (temporalmente para debug)
- ⚠️ Si no carga, revisa la consola del navegador (F12)

#### Paso 6: Iniciar Análisis
1. Click en botón **"▶️ Iniciar"** (rojo)
2. Verificar que:
   - ✅ Backend inicia procesamiento
   - ✅ WebSocket comienza a recibir eventos
   - ✅ Panel de logs muestra detecciones

#### Paso 7: Ver Detecciones en Tiempo Real
El panel de logs debería mostrar:
```
14:25:18 tipo: auto, placa ABC-1234...........
14:25:20 tipo: camión, placa desconocida.......
14:25:22 tipo: camioneta, placa XYZ-5678.......
```

### 3. Consola del Navegador (F12)

Busca estos logs:
```javascript
📥 Cargando análisis: 1
🎥 Video URL: http://localhost:8001/media/traffic_videos/...
✅ Video cargado correctamente
🔌 Conectando a WebSocket: ws://localhost:8001/ws/traffic/analysis/1/
✅ WebSocket conectado
📨 Mensaje recibido [vehicle_detected]: {...}
```

### 4. Consola del Backend

Busca estos logs:
```python
✅ Video guardado: traffic_videos/20251013_142530_Traffic_Flow...
✅ TrafficAnalysis creado: ID=1
🚗 Vehicle detected: track_id=1, type=car, plate=ABC-1234
📡 Sending WebSocket event: vehicle_detected
```

## 🐛 Troubleshooting

### Error: "Error subiendo el video"
**Causa:** Backend no está corriendo o no responde
**Solución:**
```powershell
cd backend
python manage.py runserver 0.0.0.0:8001
```

### Error: "Cannot find path .../media/..."
**Causa:** Carpeta media no existe
**Solución:**
```powershell
mkdir backend\media\traffic_videos
```

### Error: Video no se carga
**Causa:** URL incorrecta o archivo no existe
**Solución:**
1. Verifica la consola: `F12 → Console`
2. Copia la Video URL del panel azul
3. Pégala directamente en el navegador
4. Debería descargar/mostrar el video

### Error: WebSocket no conecta
**Causa:** Configuración de WebSocket incorrecta
**Solución:**
1. Verifica `VITE_WS_URL` en `.env`
2. Debería ser: `localhost:8001`

### No se detectan placas
**Causa:** EasyOCR no está instalado o el video no tiene placas legibles
**Solución:**
```powershell
pip install easyocr
```

## 📊 Verificación de Éxito

### ✅ Checklist Final
- [ ] Backend corriendo en puerto 8001
- [ ] Frontend corriendo en puerto 5175
- [ ] Video se sube correctamente (sin errores)
- [ ] Redirección a `/camera/:id` funciona
- [ ] Panel azul muestra Análisis ID y Video URL
- [ ] Video se carga en el reproductor
- [ ] Click en "Iniciar" inicia el procesamiento
- [ ] Panel de logs muestra detecciones en tiempo real
- [ ] Logs incluyen tipo de vehículo y placa (si detecta)

### 🎯 Resultado Esperado

```
Panel de Información:
┌─────────────────────────────────────┐
│ UBICACIÓN: Ciudadela Alfonso        │
│ INICIO: 13/10/2025:14:25           │
│ TIEMPO: 0h0m5s                      │
│ ELMENT. CONTADO: 3                  │
└─────────────────────────────────────┘

Panel de Logs:
┌─────────────────────────────────────┐
│ 14:25:18 tipo: auto, placa ABC-1234 │
│ 14:25:20 tipo: camión, placa N/A    │
│ 14:25:22 tipo: camioneta, placa XYZ │
└─────────────────────────────────────┘
```

## 🚀 Próximos Pasos

Una vez verificado el flujo básico:
1. Deshabilitar controles del video (`controls={false}`)
2. Sincronizar video con análisis frame-by-frame
3. Agregar visualización de bounding boxes
4. Implementar filtros de búsqueda por placa
5. Generar reportes estadísticos
