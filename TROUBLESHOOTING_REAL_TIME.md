# 🔧 Troubleshooting - Video no se procesa en tiempo real

## ❌ Problema: "Le di iniciar pero no muestra el video procesándose"

### ✅ SOLUCIÓN PASO A PASO:

## 1️⃣ VERIFICAR CELERY (MÁS IMPORTANTE)

**El problema #1 más común es que Celery NO está corriendo.**

### Abrir nueva terminal PowerShell:
```powershell
cd s:\Construccion\SIMPTV\backend
celery -A config worker -l info --pool=solo
```

### ✅ Deberías ver:
```
-------------- celery@TU_PC v5.x.x
---- **** -----
--- * ***  * -- Windows-10-10.0.xxxxx
-- * - **** ---
- ** ---------- [config]
- ** ---------- .> app:         config:0x...
- ** ---------- .> transport:   redis://localhost:6379//
- ** ---------- .> results:     redis://localhost:6379/
- *** --- * --- .> concurrency: 1 (solo)
-- ******* ---- .> task events: OFF

[tasks]
  . apps.traffic_app.tasks.process_video_analysis

[2025-10-13 XX:XX:XX,XXX: INFO/MainProcess] Connected to redis://localhost:6379//
[2025-10-13 XX:XX:XX,XXX: INFO/MainProcess] mingle: searching for neighbors
[2025-10-13 XX:XX:XX,XXX: INFO/MainProcess] mingle: all alone
[2025-10-13 XX:XX:XX,XXX: INFO/MainProcess] celery@TU_PC ready.
```

### ❌ Si ves errores:
- **"Cannot connect to redis"**: Redis no está corriendo (ver paso 2)
- **"ModuleNotFoundError"**: Entorno virtual no activado
- **"No module named 'config'"**: Estás en el directorio incorrecto

---

## 2️⃣ VERIFICAR REDIS

### Abrir nueva terminal PowerShell:
```powershell
cd s:\Construccion\SIMPTV\backend\redis
.\redis-server.exe redis.windows.conf
```

### ✅ Deberías ver:
```
                _._                                                  
           _.-``__ ''-._                                             
      _.-``    `.  `_.  ''-._           Redis 7.x.x (xxxxx/0) 64 bit
  .-`` .-```.  ```\/    _.,_ ''-._                                  
 (    '      ,       .-`  | `,    )     Running in standalone mode
 |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
 |    `-._   `._    /     _.-'    |     PID: XXXX
  `-._    `-._  `-./  _.-'    _.-'                                   
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |                                  
  `-._    `-._`-.__.-'_.-'    _.-'                                   
      `-._    `-.__.-'    _.-'                                       
          `-._        _.-'                                           
              `-.__.-'                                               

Server initialized
Ready to accept connections tcp
```

---

## 3️⃣ VERIFICAR BACKEND DJANGO

### Terminal ya debería estar corriendo:
```powershell
cd s:\Construccion\SIMPTV\backend
python manage.py runserver 8001
```

### ✅ Deberías ver:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
October 13, 2025 - XX:XX:XX
Django version 5.x.x, using settings 'config.settings'
Starting development server at http://127.0.0.1:8001/
Quit the server with CTRL-BREAK.
```

---

## 4️⃣ HACER CLIC EN INICIAR Y VERIFICAR LOGS

### En la consola del navegador (F12 → Console):

**Al hacer clic en Iniciar, deberías ver:**
```javascript
✅ Análisis iniciado: {analysis_id: 4, ...}
▶️ Mostrando frames procesados con YOLOv8 + OCR
✅ WebSocket conectado para análisis: 4
```

**Cuando lleguen frames:**
```javascript
📸 Frame recibido: 30 detecciones: 5
✅ Frame dibujado en canvas: 1920 x 1080
🚗 Vehículo detectado (raw): {track_id: "...", vehicle_type: "car", ...}
✅ Detección formateada: {timestamp: "...", vehicleType: "car", ...}
📋 Total detecciones ahora: 1
```

### ❌ Si ves en consola:
- **"WebSocket connection to 'ws://localhost:8001/ws/traffic/analysis/4/' failed"**
  → El backend no está corriendo en puerto 8001
  
- **"No hay análisis disponible para iniciar"**
  → No hay analysisId en la página
  
- **"Error al iniciar/reanudar análisis"**
  → El endpoint `/api/traffic/analysis/{id}/start/` falló (ver logs del backend)

---

## 5️⃣ VERIFICAR TERMINAL DE CELERY (CRÍTICO)

**Cuando hagas clic en Iniciar, en la terminal de Celery deberías ver:**

```
[2025-10-13 XX:XX:XX,XXX: INFO/MainProcess] Task apps.traffic_app.tasks.process_video_analysis[xxxxx] received
[2025-10-13 XX:XX:XX,XXX: INFO/ForkPoolWorker-1] Starting video analysis task for ID: 4
📹 Iniciando procesamiento de video: s:\Construccion\SIMPTV\backend\media\traffic_videos\20251013_065032_Traffic Flow...mp4
🚀 VideoProcessor usando device: cuda
🔤 Inicializando EasyOCR para detección de placas...
✅ EasyOCR inicializado correctamente
📊 Video info: 1920x1080, 30 FPS, 9000 frames

[... procesando frames ...]

🚗 Vehicle detected: track_id=ckxxxxxx, type=car
🔤 Placa detectada: ABC-1234 (Vehículo: car, Confianza: 95.3%)
```

### ❌ Si NO ves nada en Celery:
1. **Celery NO está corriendo** (volver al paso 1)
2. **El endpoint `/start/` falló** (verificar logs del backend Django)
3. **Redis no está conectado** (volver al paso 2)

---

## 6️⃣ VERIFICAR LOGS DEL BACKEND DJANGO

**En la terminal donde corre Django, cuando hagas clic en Iniciar:**

```
[13/Oct/2025 XX:XX:XX] "POST /api/traffic/analysis/4/start/ HTTP/1.1" 200 XXX
```

### ❌ Si ves error 400 o 500:
```
[13/Oct/2025 XX:XX:XX] "POST /api/traffic/analysis/4/start/ HTTP/1.1" 400 XXX
```
→ Revisar el error específico en la terminal (debería imprimir el mensaje de error)

---

## 7️⃣ VERIFICAR CANVAS EN EL NAVEGADOR

### Inspeccionar elemento (F12 → Elements):

Buscar el `<canvas>` en el código HTML:
```html
<canvas class="w-full h-full object-contain block" style="background-color: rgb(0, 0, 0);" width="1920" height="1080"></canvas>
```

**Verificar:**
- ✅ `class` incluye `"block"` (visible)
- ✅ `width` y `height` tienen valores (ej: 1920x1080)
- ✅ Canvas NO está vacío (debería tener una imagen dibujada)

### ❌ Si el canvas está vacío:
1. Celery no está enviando frames (volver al paso 5)
2. WebSocket no está conectado (volver al paso 4)
3. El canvas tiene `class="... hidden"` → `showProcessedFrames` es `false`

---

## 8️⃣ CHECKLIST RÁPIDO

Antes de hacer clic en Iniciar, verifica:

| # | Servicio | ¿Está corriendo? | ¿Cómo verificar? |
|---|----------|------------------|------------------|
| 1 | **Redis** | ✅ / ❌ | Terminal muestra "Ready to accept connections" |
| 2 | **Celery Worker** | ✅ / ❌ | Terminal muestra "celery@PC ready" |
| 3 | **Django Backend** | ✅ / ❌ | Terminal muestra "Starting development server at http://127.0.0.1:8001/" |
| 4 | **Frontend React** | ✅ / ❌ | Navegador en http://localhost:5174/camera/2 |
| 5 | **Video cargado** | ✅ / ❌ | Se ve el video en la página (aunque no se reproduce) |
| 6 | **WebSocket conectado** | ✅ / ❌ | Consola muestra "✅ WebSocket conectado para análisis: X" |

**SI TODOS SON ✅, haz clic en Iniciar y deberías ver:**
- Badge rojo "PROCESANDO EN TIEMPO REAL"
- Canvas muestra frames con cajas de colores
- Panel verde muestra detecciones

---

## 🐛 ERRORES COMUNES Y SOLUCIONES

### Error: "Cannot connect to redis"
**Causa:** Redis no está corriendo  
**Solución:** Iniciar Redis (paso 2)

### Error: "Video file not found"
**Causa:** El video no se subió correctamente  
**Solución:** Volver a subir el video desde /traffic

### Error: "No module named 'ultralytics'"
**Causa:** Dependencias de Python no instaladas  
**Solución:** 
```powershell
cd s:\Construccion\SIMPTV\backend
pip install -r requirements.txt
```

### Error: "ModuleNotFoundError: No module named 'easyocr'"
**Causa:** EasyOCR no está instalado  
**Solución:**
```powershell
cd s:\Construccion\SIMPTV\backend
pip install easyocr
```

### Error: Canvas negro, no muestra frames
**Causa:** Celery no está corriendo o no está procesando  
**Solución:** 
1. Verificar que Celery esté corriendo (paso 1)
2. Verificar logs de Celery para ver si está procesando frames
3. Verificar consola del navegador para ver si llegan frames

### Error: "Esperando detecciones..." nunca cambia
**Causa:** No se están detectando vehículos O Celery no está corriendo  
**Solución:**
1. Verificar que Celery esté corriendo (paso 1)
2. Esperar más tiempo (procesamiento toma tiempo)
3. Verificar logs de Celery: debe mostrar "🚗 Vehicle detected"
4. Verificar consola navegador: debe mostrar "🚗 Vehículo detectado (raw)"

---

## 📞 COMANDO DE DIAGNÓSTICO RÁPIDO

### PowerShell:
```powershell
# Verificar si Redis está corriendo
Get-Process redis-server -ErrorAction SilentlyContinue

# Verificar si Python (Django) está corriendo en puerto 8001
Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue

# Verificar si Celery está corriendo
Get-Process -Name "celery" -ErrorAction SilentlyContinue
```

---

## 📚 RECURSOS ADICIONALES

- **Documentación completa:** `REAL_TIME_PROCESSING_IMPLEMENTATION.md`
- **Script de inicio:** `START_ALL_SERVICES.ps1`
- **Guía de setup:** `START_ANALYSIS_GUIDE.md`

---

## 💡 TIP FINAL

**El 90% de los problemas se resuelven asegurándose de que Celery esté corriendo correctamente.**

Si después de seguir todos los pasos aún no funciona, comparte:
1. Logs completos de Celery (toda la terminal)
2. Logs de la consola del navegador (F12 → Console)
3. Logs del backend Django cuando haces clic en Iniciar
