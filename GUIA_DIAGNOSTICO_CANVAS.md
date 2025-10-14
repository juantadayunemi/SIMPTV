# 🚨 CANVAS NEGRO - GUÍA DE DIAGNÓSTICO

## 📋 Situación Actual

✅ **Lo que FUNCIONA:**
- El botón "Iniciar" responde (badge rojo "PROCESANDO EN TIEMPO REAL" aparece)
- El backend acepta la petición (200 OK)
- El estado cambia a PROCESSING

❌ **Lo que NO funciona:**
- Canvas está completamente NEGRO (debería mostrar video con boxes)
- Panel dice "Esperando detecciones..." (debería mostrar lista de vehículos)

---

## 🔍 DIAGNÓSTICO PASO A PASO

### PASO 1: Ver Logs de Django 🔴 MUY IMPORTANTE

**Qué hacer:**
1. Ve a la terminal donde corre Django (puerto 8001)
2. Después de hacer clic en "Iniciar", deberías ver esta secuencia:

```
[DD/Mon/YYYY HH:MM:SS] "POST /api/traffic/analysis/4/start/ HTTP/1.1" 200 XXX
🚀 Lanzando procesamiento para análisis 4
✅ Thread de procesamiento iniciado
🔄 run_processing() iniciado para análisis 4
⚠️ Celery no disponible: [error]
🎬 Ejecutando runner standalone para análisis 4...
✅ Módulo runner importado correctamente

============================================================
🎬 STANDALONE: Iniciando análisis 4
============================================================

📊 Cargando análisis 4 desde DB...
✅ Análisis cargado: traffic_videos/...
📹 Iniciando análisis: traffic_videos/...
✅ Video encontrado: 23.67MB
🚀 Inicializando VideoProcessor...
   - Model path: backend/models/yolov8n.pt
   - Confidence: 0.5, IOU: 0.45

[ESPERA 20-40 SEGUNDOS - EasyOCR se está cargando]

✅ VideoProcessor inicializado (YOLOv8 + EasyOCR cargados)
📹 Iniciando procesamiento de video: ...
📊 Video info: 1920x1080, 30 FPS, XXXX frames

🎬 Iniciando procesamiento de video...
   - Video: S:\...\traffic_videos\...
   - Callbacks configurados: progress ✅, frame ✅

📹 Frame 30 procesado, 5 detecciones
🚀 Primer frame enviado a WebSocket (frame #3)
📹 Frame 60 procesado, 3 detecciones
🚗 Vehículo detectado: ck123456 (car)
🔤 Placa detectada: ABC-1234 (Vehículo: car, Confianza: 89.5%)
```

---

### ❌ CASO 1: NO ves el banner de "STANDALONE: Iniciando análisis 4"

**Problema:** El thread NO se está ejecutando

**Causa probable:**
- Error al importar `video_analysis_runner.py`
- Excepción silenciosa en el thread

**Solución:**
Comparte el error que aparece en la terminal Django después de:
```
🎬 Ejecutando runner standalone para análisis 4...
```

---

### ❌ CASO 2: Ves "STANDALONE: Iniciando" pero se detiene en "Inicializando VideoProcessor"

**Problema:** YOLOv8 o EasyOCR no se pueden cargar

**Causa probable:**
- Modelo yolov8n.pt no existe en `backend/models/`
- EasyOCR no está instalado
- GPU/CUDA tiene problemas

**Solución:**
Ejecuta esto en terminal:
```powershell
cd backend
python -c "import torch; print('CUDA disponible:', torch.cuda.is_available())"
python -c "import easyocr; print('EasyOCR OK')"
python -c "from ultralytics import YOLO; print('YOLOv8 OK')"
```

---

### ❌ CASO 3: Ves todo hasta "VideoProcessor inicializado" pero NO ves "Frame 30 procesado"

**Problema:** El video no se puede abrir o el procesamiento falla

**Causa probable:**
- Video corrupto
- OpenCV no puede leer el codec del video
- Error en `process_video()`

**Solución:**
Ejecuta:
```powershell
cd backend
python -c "import cv2; cap = cv2.VideoCapture('media/traffic_videos/20251013_071307_Traffic Flow In The Highway - 4K Stock Videos   NoCopyright   AllVideoFree.mp4'); print('Video abre:', cap.isOpened()); print('Total frames:', int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))"
```

---

### ❌ CASO 4: Ves "Primer frame enviado a WebSocket" pero el canvas sigue NEGRO

**Problema:** WebSocket no está conectado o el frontend no recibe los eventos

**Solución:** Ir al PASO 2 (Consola del Navegador)

---

## PASO 2: Ver Consola del Navegador 🌐

**Qué hacer:**
1. En el navegador, presiona **F12**
2. Ve a la pestaña **Console**
3. Haz clic en "Iniciar"
4. Deberías ver:

```
✅ Análisis iniciado: Object { id: 4, status: "PROCESSING", ... }
▶️ Mostrando frames procesados con YOLOv8 + OCR
🔌 Conectando a WebSocket: ws://localhost:8001/ws/traffic/analysis/4/
✅ WebSocket conectado para análisis: 4
📸 Frame recibido: 3 detecciones: 5
✅ Frame dibujado en canvas: 1920 x 1080
📸 Frame recibido: 6 detecciones: 3
✅ Frame dibujado en canvas: 1920 x 1080
🚗 Vehículo detectado (raw): Object { track_id: "ck123", vehicle_type: "car", ... }
```

---

### ❌ CASO A: "WebSocket connection failed"

**Problema:** Django Channels no está corriendo o hay error en routing

**Solución:**
1. Verifica que Django esté corriendo en puerto 8001
2. Verifica que uses `python manage.py runserver` (NO usar `daphne`)
3. Comparte el error completo del WebSocket

---

### ❌ CASO B: WebSocket conecta pero NO ves "Frame recibido"

**Problema:** Los eventos NO llegan del backend al frontend

**Posibles causas:**
1. InMemoryChannelLayer no está configurado correctamente
2. El `send_websocket_event()` tiene un error
3. El consumer no está enviando los frames

**Solución:**
En la terminal Django, busca:
```
🌐 Consumer enviando frame_update: frame #3
```

Si NO ves ese mensaje, el problema está en el channel layer.

---

### ❌ CASO C: Ves "Frame recibido" pero NO se dibuja en canvas

**Problema:** Canvas no existe o el código de dibujo falla

**Solución:**
En la consola del navegador (F12 → Elements), busca:
```html
<canvas id="videoCanvas"></canvas>
```

Si el canvas NO existe, hay un problema en React.

---

## 🔧 ACCIONES INMEDIATAS

### 1️⃣ Ejecuta el script de diagnóstico:

```powershell
cd backend
python diagnose_canvas.py
```

### 2️⃣ Reinicia Django con los nuevos logs:

```powershell
# Ctrl+C en la terminal Django
cd backend
python manage.py runserver 8001
```

### 3️⃣ Refresca el navegador:

- Ve a http://localhost:5174/camera/2
- Presiona F5
- Abre la consola (F12)
- Haz clic en "Iniciar"

### 4️⃣ Comparte capturas de:

1. **Terminal Django** (todo el output después de hacer clic en Iniciar)
2. **Consola del navegador** (F12 → Console, todo el output)
3. Si hay errores, **Network tab** (F12 → Network, WebSocket connections)

---

## 📊 INFORMACIÓN ADICIONAL

### Tiempos esperados:

- **Carga de YOLOv8:** ~2-5 segundos
- **Carga de EasyOCR:** ~20-40 segundos (primera vez)
- **Primer frame enviado:** ~30-50 segundos después de hacer clic
- **Primer vehículo detectado:** ~30-90 segundos (depende del video)

### ¿Qué deberías ver en el canvas?

- Video en tiempo real (no estático)
- Cajas de colores alrededor de vehículos:
  - **Cyan (celeste):** cars
  - **Rojo:** trucks
  - **Magenta:** motorcycles
  - **Verde:** buses
- Labels arriba de cada caja: "car 0.95"
- Labels azules abajo: "Number Plate: ABC-1234" (si detecta placa)

---

## ✅ SIGUIENTE PASO

**POR FAVOR, COMPARTE:**
1. Output completo de la terminal Django después de hacer clic en "Iniciar"
2. Output completo de la consola del navegador (F12)

Con esa información podré identificar exactamente dónde está el problema. 🔍
