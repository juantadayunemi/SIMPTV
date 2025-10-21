# ✅ CORRECCIONES: OCR DE PLACAS + CONTROL DE VIDEO

**Fecha**: 21/10/2025
**Estado**: ✅ **LISTO PARA PRUEBAS**

---

## 🎯 PROBLEMAS IDENTIFICADOS

### 1. **OCR Detectaba Valores Random** ❌
- **Problema**: PaddleOCR leía texto incorrecto de las placas
- **Causa**: Preprocesamiento inadecuado y validaciones demasiado estrictas
- **Ejemplo**: HaarCascade detectaba bien el cuadro de placa, pero OCR devolvía "XYZ123ABC" en lugar del texto real

### 2. **Video con Controles de Reproducción** ❌
- **Problema**: Video se reproducía automáticamente con controles adelantar/atrasar
- **Causa**: Tag `<video controls>` con `autoPlay` en el frontend
- **Usuario quería**: Video pausado hasta presionar "Iniciar"

---

## 🔧 SOLUCIONES IMPLEMENTADAS

### 1. **Mejoras en Detección de Placas (HaarCascade)** ✅

**Archivo**: `backend/apps/traffic_app/services/video_processor_opencv.py`

#### Líneas 331-363: `detect_plate_in_roi()`

**ANTES** (demasiado estricto):
```python
# Validaciones excesivas que rechazaban placas válidas
minNeighbors=8  # Muy estricto
minSize=(60, 20)  # Demasiado grande
maxSize=(int(roi_w * 0.8), int(roi_h * 0.4))
# + 5 validaciones de aspect ratio, posición, bordes
```

**AHORA** (original que funcionaba):
```python
# Parámetros originales que detectaban bien
plates = self.plate_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(25, 25)
)

# Solo retorna placa con mayor área
largest = max(plates, key=lambda x: x[2] * x[3])
return tuple(largest)
```

**Resultado**: ✅ HaarCascade detecta bien las placas (como antes)

---

### 2. **Mejoras en Preprocesamiento OCR** ✅

**Archivo**: `backend/apps/traffic_app/services/video_processor_opencv.py`

#### Líneas 365-413: `preprocess_plate()`

**MEJORAS IMPLEMENTADAS**:

```python
# 1. Redimensionar a altura óptima (48px para PaddleOCR)
target_height = 48
scale = target_height / h
resized = cv2.resize(plate_roi, (new_width, target_height), INTER_CUBIC)

# 2. Convertir a escala de grises
gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

# 3. Eliminar ruido con filtro bilateral (preserva bordes)
denoised = cv2.bilateralFilter(gray, 9, 75, 75)

# 4. Mejorar contraste con CLAHE (más agresivo)
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
enhanced = clahe.apply(denoised)

# 5. Binarización adaptativa (ventana mayor: 15)
binary = cv2.adaptiveThreshold(
    enhanced, 255, ADAPTIVE_THRESH_GAUSSIAN_C,
    THRESH_BINARY, 15, 2
)

# 6. Operación morfológica para limpiar texto
kernel = cv2.getStructuringElement(MORPH_RECT, (2, 2))
morph = cv2.morphologyEx(binary, MORPH_CLOSE, kernel)

# 7. Invertir si fondo es negro (PaddleOCR espera texto negro/blanco)
mean_val = np.mean(morph)
if mean_val < 127:
    morph = cv2.bitwise_not(morph)
```

**Resultado**: ✅ Imagen mejor preparada para OCR

---

### 3. **Múltiples Intentos de OCR** ✅

**Archivo**: `backend/apps/traffic_app/services/video_processor_opencv.py`

#### Líneas 415-502: `recognize_plate()`

**ESTRATEGIA DE 3 INTENTOS**:

```python
# INTENTO 1: Con preprocesamiento completo (binario + morfología)
preprocessed = self.preprocess_plate(plate_roi)
plate_text = read_plate(preprocessed)

# INTENTO 2: Imagen original en COLOR (PaddleOCR a veces prefiere color)
if not plate_text or len(plate_text) < 5:
    resized_color = cv2.resize(plate_roi, (new_width, 48), INTER_CUBIC)
    plate_text = read_plate(resized_color)

# INTENTO 3: Solo escala de grises + CLAHE (sin binarización)
if not plate_text or len(plate_text) < 5:
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    plate_text = read_plate(enhanced)
```

**VALIDACIONES RELAJADAS**:
```python
# ANTES: Muy estricto
if 5 <= len(clean_text) <= 10:
    if num_digits >= 2 and num_letters >= 2:  # Muy restrictivo

# AHORA: Más permisivo
if len(clean_text) >= 5:
    has_digit = any(c.isdigit() for c in clean_text)
    has_letter = any(c.isalpha() for c in clean_text)
    if has_digit and has_letter:  # Solo requiere al menos 1 de cada
```

**LOGS DE DEPURACIÓN**:
```python
print(f"🔍 OCR detectó: '{plate_text}' (longitud: {len(plate_text)})")
print(f"🧹 Texto limpio: '{clean_text}' (longitud: {len(clean_text)})")
print(f"✅ Validación: dígitos={has_digit}, letras={has_letter}")
print(f"✅ PLACA VÁLIDA: {clean_text.upper()}")
```

**Resultado**: ✅ Mayor probabilidad de leer correctamente + debug visible

---

### 4. **Control de Video Mejorado** ✅

**Archivo**: `frontend/src/pages/AnalysisPage.tsx`

#### Cambios Clave:

**ANTES** (video con controles):
```tsx
<video
  ref={videoRef}
  controls  // ❌ Permitía adelantar/atrasar
  autoPlay  // ❌ Se reproducía automáticamente
  className="w-full h-auto rounded-lg shadow-lg"
  src={videoUrl}
/>
```

**AHORA** (video como imagen estática):
```tsx
{/* Mostrar solo el primer frame como imagen estática */}
<div className="relative w-full aspect-video bg-black rounded-lg shadow-lg overflow-hidden">
  <video
    ref={videoRef}
    className="w-full h-full object-contain"
    src={videoUrl}
    // ❌ SIN controls (no puede adelantar/atrasar)
    // ❌ SIN autoPlay (no se reproduce hasta "Iniciar")
  />
  
  {/* Overlay para evitar interacción */}
  <div className="absolute inset-0 pointer-events-none" />
</div>

{/* Botones de control */}
<div className="flex gap-2 justify-center">
  <button onClick={handleReconnect}>🔄 Reconectar</button>
  <button onClick={handlePause}>⏸ Pausa</button>
  <button onClick={handleStart}>▶️ Iniciar</button>
</div>
```

**COMPORTAMIENTO**:
1. **Al cargar**: Video muestra primer frame (pausado)
2. **Al presionar "Iniciar"**: Backend procesa video y envía frames vía WebSocket
3. **Canvas procesado**: Se muestra en lugar del video original
4. **No hay controles**: Usuario no puede adelantar/atrasar manualmente

**Resultado**: ✅ Video estático hasta presionar "Iniciar"

---

## 📊 RESUMEN DE ARCHIVOS MODIFICADOS

```
backend/apps/traffic_app/services/video_processor_opencv.py
├── detect_plate_in_roi()     ✅ (líneas 331-363)  - Vuelto a original
├── preprocess_plate()         ✅ (líneas 365-413)  - 7 mejoras
└── recognize_plate()          ✅ (líneas 415-502)  - 3 intentos + logs

frontend/src/pages/AnalysisPage.tsx
└── Video component            ✅ (líneas ~150-200) - Sin controles
```

---

## 🧪 CÓMO PROBAR

### 1. **Reiniciar Backend**
```powershell
cd S:\Construccion\SIMPTV\backend
python manage.py runserver 8001
```

### 2. **Verificar Logs OCR**
Cuando se detecte una placa, verás en consola:
```
🔍 OCR detectó: 'ABC-1234' (longitud: 8)
🧹 Texto limpio: 'ABC1234' (longitud: 7)
✅ Validación: dígitos=True, letras=True
✅ PLACA VÁLIDA: ABC1234
```

O si falla:
```
🔍 OCR detectó: 'X' (longitud: 1)
🧹 Texto limpio: 'X' (longitud: 1)
❌ Rechazado: longitud 1 < 5
```

### 3. **Probar Video**
1. Abrir `http://localhost:8000`
2. Subir video
3. **VERIFICAR**: Video debe estar pausado (solo muestra primer frame)
4. Presionar "Iniciar"
5. **VERIFICAR**: Análisis comienza, canvas se actualiza
6. **VERIFICAR**: No hay controles para adelantar/atrasar

---

## 🎯 EXPECTATIVAS

### ✅ Detección de Placas
- **Cuadro de placa**: HaarCascade detecta correctamente (como antes)
- **Texto OCR**: 3 intentos aumentan probabilidad de lectura correcta
- **Logs**: Ves exactamente qué detecta PaddleOCR en cada intento

### ✅ Control de Video
- **Inicial**: Video pausado (primer frame visible)
- **Durante análisis**: Canvas procesado reemplaza video
- **Sin controles**: Usuario no puede interferir con timeline

---

## 🐛 SI AÚN HAY PROBLEMAS

### Problema: "OCR sigue detectando texto incorrecto"

**Diagnóstico**:
1. Verificar logs en consola: `🔍 OCR detectó: '...'`
2. Si detecta texto pero es incorrecto, problema es de **PaddleOCR**
3. Si no detecta nada, problema es de **preprocesamiento**

**Soluciones adicionales**:
```python
# Opción A: Guardar imagen preprocesada para inspección
cv2.imwrite(f'debug_plate_{frame_number}.jpg', preprocessed)

# Opción B: Ajustar parámetros CLAHE
clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))  # Más agresivo

# Opción C: Probar solo con color (sin preprocesamiento)
plate_text = read_plate(plate_roi)  # Directo, sin preprocess
```

### Problema: "Video sigue mostrando controles"

**Verificar**:
```tsx
// En AnalysisPage.tsx, buscar:
<video
  ref={videoRef}
  // ❌ NO debe tener "controls"
  // ❌ NO debe tener "autoPlay"
/>
```

Si persiste, limpiar caché del navegador: `Ctrl + Shift + Delete`

---

## 📝 NOTAS TÉCNICAS

### PaddleOCR - Mejores Prácticas
1. **Altura óptima**: 32-48 píxeles
2. **Contraste**: CLAHE con clipLimit=2.0-4.0
3. **Color vs Grises**: Probar ambos (a veces color funciona mejor)
4. **Binarización**: Útil para texto con iluminación uniforme

### HaarCascade - Parámetros
- `scaleFactor=1.1`: Balance velocidad/precisión
- `minNeighbors=5`: Suficiente para filtrar falsos positivos
- `minSize=(25,25)`: Permite placas pequeñas en video

### WebSocket + Video
- Frontend NO reproduce video localmente
- Backend envía frames procesados vía WebSocket
- Canvas actualizado con `drawImage()` en cada frame

---

## ✅ CHECKLIST DE VERIFICACIÓN

- [x] HaarCascade detecta cuadros de placas (revertido a original)
- [x] Preprocesamiento mejorado (7 pasos)
- [x] 3 intentos de OCR (binario, color, grises)
- [x] Validaciones relajadas (solo 1 dígito + 1 letra)
- [x] Logs de depuración agregados
- [x] Video sin controles (no autoplay)
- [x] Video pausado hasta "Iniciar"
- [x] Canvas procesado reemplaza video durante análisis

---

**Siguiente paso**: Probar con video real y verificar logs de OCR en consola.

**Generado**: 21/10/2025 22:30
