# ✅ GUÍA RÁPIDA - Hacer Funcionar el Procesamiento en Tiempo Real

## 🎯 Estado Actual:
- ✅ Análisis reseteado a PENDING
- ✅ Código actualizado con mejor logging
- ✅ Runner standalone implementado

## 🚀 PASOS PARA HACER FUNCIONAR:

### 1️⃣ REINICIAR BACKEND DJANGO (IMPORTANTE)

**En la terminal donde corre Django, presionar Ctrl+C y luego:**

```powershell
cd s:\Construccion\SIMPTV\backend
python manage.py runserver 8001
```

**⚠️ CRÍTICO:** Sin reiniciar, los cambios nuevos no se cargan.

---

### 2️⃣ REFRESCAR NAVEGADOR

**En el navegador:**
1. Ir a: http://localhost:5174/camera/2
2. Presionar F5 para refrescar
3. Abrir consola del navegador (F12)

---

### 3️⃣ HACER CLIC EN "INICIAR"

**Click en el botón verde "▶️ Iniciar"**

---

### 4️⃣ VERIFICAR EN TERMINAL DE DJANGO

**Deberías ver esto inmediatamente:**

```
[DD/Mon/YYYY HH:MM:SS] "POST /api/traffic/analysis/4/start/ HTTP/1.1" 200 XXX
🚀 Lanzando procesamiento para análisis 4
✅ Thread de procesamiento iniciado
🔄 run_processing() iniciado para análisis 4
🚀 Intentando Celery...
⚠️ Celery no disponible: <error de Celery>
🎬 Ejecutando runner standalone para análisis 4...
✅ Módulo runner importado correctamente
🎬 STANDALONE: Iniciando análisis 4
📹 Iniciando análisis: traffic_videos/20251013_071307_Traffic Flow...
✅ Video encontrado: XX.XXMB
🚀 VideoProcessor usando device: cuda (o cpu)
🔤 Inicializando EasyOCR para detección de placas...
```

**Esperar ~30 segundos mientras carga EasyOCR, luego:**

```
✅ EasyOCR inicializado correctamente
✅ YOLOv8 + OCR cargados
📊 Video info: 1920x1080, 30 FPS, XXXX frames
🎬 Iniciando procesamiento de video...
```

**Y después, cada vez que detecte vehículos:**

```
🚗 Vehículo detectado: ckxxxxxx (car)
🔤 Placa detectada: ABC-1234 (Vehículo: car, Confianza: 95.3%)
```

---

### 5️⃣ VERIFICAR EN CONSOLA DEL NAVEGADOR (F12)

**Deberías ver:**

```javascript
✅ Análisis iniciado: Object { analysis_id: 4, ... }
▶️ Mostrando frames procesados con YOLOv8 + OCR
✅ WebSocket conectado para análisis: 4
```

**Y cuando lleguen frames:**

```javascript
📸 Frame recibido: 30 detecciones: 5
✅ Frame dibujado en canvas: 1920 x 1080
🚗 Vehículo detectado (raw): Object { track_id: "ck...", vehicle_type: "car", ... }
✅ Detección formateada: Object { timestamp: "...", vehicleType: "car", ... }
📋 Total detecciones ahora: 1
```

---

### 6️⃣ VERIFICAR EN LA PÁGINA WEB

**Deberías ver:**

1. ✅ **Badge rojo pulsante:** "PROCESANDO EN TIEMPO REAL"
2. ✅ **Canvas (área negra):** Se llena con frames del video mostrando:
   - Cajas de colores alrededor de vehículos (cyan=auto, rojo=camión)
   - Texto arriba de cada caja: "car 0.95"
   - Texto con fondo azul debajo: "Number Plate: ABC-1234"
3. ✅ **Panel verde (abajo):** En lugar de "Esperando detecciones...", muestra:
   - "14:25:18 tipo: car, placa ABC-1234"
   - "14:25:19 tipo: truck, placa XYZ-5678"
   - Scroll automático a las últimas

---

## 🐛 TROUBLESHOOTING

### ❌ NO veo mensajes en terminal Django

**Solución:**
1. Presiona Ctrl+C en terminal Django
2. Ejecuta de nuevo: `python manage.py runserver 8001`
3. Espera a que cargue completamente
4. Refresca navegador (F5)
5. Click en "Iniciar" de nuevo

---

### ❌ Canvas sigue NEGRO después de hacer clic

**Posibles causas:**

1. **Backend no reiniciado**
   - Solución: Reiniciar Django (ver arriba)

2. **WebSocket no conectado**
   - Verificar consola navegador (F12): debe decir "✅ WebSocket conectado"
   - Si dice error de WebSocket, reiniciar Django

3. **Procesamiento no se inició**
   - Verificar terminal Django: debe mostrar "🎬 STANDALONE: Iniciando análisis"
   - Si NO aparece, hay un error en el código

4. **Video no existe**
   - Terminal Django mostraría: "❌ Error: Video no encontrado"
   - Solución: Volver a subir video desde /traffic

---

### ❌ "Esperando detecciones..." NO cambia

**Solución:**

1. **Espera 30-60 segundos:** Cargar YOLOv8 + EasyOCR toma tiempo
2. **Verifica terminal Django:** Debe mostrar "🚗 Vehículo detectado"
3. **Verifica consola navegador:** Debe mostrar "🚗 Vehículo detectado (raw)"
4. Si NO aparecen detecciones después de 2 minutos:
   - El video puede no tener vehículos visibles al inicio
   - O hay un error en el procesamiento (revisar terminal Django)

---

### ❌ Error "ModuleNotFoundError: No module named 'ultralytics'"

**Solución:**
```powershell
cd s:\Construccion\SIMPTV\backend
pip install ultralytics easyocr opencv-python
```

Luego reiniciar Django.

---

### ❌ Error "No module named 'video_analysis_runner'"

**Verificar que el archivo existe:**
```powershell
dir s:\Construccion\SIMPTV\backend\apps\traffic_app\services\video_analysis_runner.py
```

Si NO existe, hay un problema. Avísame.

---

## 📊 TIEMPO ESPERADO

- **Carga inicial (EasyOCR):** 20-40 segundos
- **Primera detección visible:** 30-90 segundos
- **Frames en canvas:** Aparecen gradualmente, ~10 frames por segundo

---

## ✅ CHECKLIST ANTES DE PROBAR

Marca cada item:

- [ ] Backend Django reiniciado con: `python manage.py runserver 8001`
- [ ] Frontend corriendo: `npm run dev`
- [ ] Navegador en: http://localhost:5174/camera/2
- [ ] Consola del navegador abierta (F12)
- [ ] Terminal de Django visible para ver logs
- [ ] Análisis reseteado a PENDING (ya está ✅)

**Si todos están marcados, haz clic en "▶️ Iniciar" y observa los logs en Django.**

---

## 💡 NOTA IMPORTANTE

El procesamiento puede tomar **varios minutos** dependiendo de:
- Longitud del video
- Poder de tu CPU/GPU
- Cantidad de vehículos en el video

**Sé paciente**, especialmente en la primera ejecución mientras carga los modelos.

---

## 📞 SI NADA FUNCIONA

Comparte:
1. **Captura de pantalla** de la terminal Django después de hacer clic en Iniciar
2. **Captura de pantalla** de la consola del navegador (F12)
3. Texto completo de cualquier error que aparezca

Con eso podré identificar exactamente qué está pasando.
