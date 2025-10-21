# 🔍 DIAGNÓSTICO: Detección de Placas No Funciona

**Fecha**: 21/10/2025 23:35
**Problema**: Caja de placa no aparece, datos de placa no se muestran

---

## 🎯 CAMBIOS APLICADOS PARA DEBUGGING

### 1. **Logs en Carga de HaarCascade**

**Archivo**: `video_processor_opencv.py` (líneas 170-189)

```python
print(f"📦 Cargando HaarCascade para detección de placas...")
print(f"   Ruta: {self.haarcascade_path}")
print(f"   Existe: {self.haarcascade_path.exists()}")

if self.haarcascade_path.exists():
    self.plate_cascade = cv2.CascadeClassifier(str(self.haarcascade_path))
    print(f"   ✅ Cargado desde archivo local")
else:
    print("⚠️  HaarCascade local no encontrado, usando OpenCV default")

if self.plate_cascade.empty():
    print("❌ ERROR CRÍTICO: HaarCascade no pudo cargarse")
else:
    print(f"✅ HaarCascade cargado correctamente")
```

---

### 2. **Logs en Detección de Placas**

**Archivo**: `video_processor_opencv.py` (líneas 564-604)

```python
if detect_plates:
    try:
        vehicle_roi = frame[y1:y2, x1:x2]
        
        if vehicle_roi.size > 0:
            plate_coords = self.detect_plate_in_roi(vehicle_roi)
            
            if plate_coords:
                print(f"🟢 HaarCascade detectó placa: ({px}, {py}, {pw}, {ph}) en vehículo {track_id}")
                
                # ... validaciones ...
                
                print(f"📸 Intentando OCR en placa {pw}x{ph}...")
                plate_text = self.recognize_plate(plate_roi)
                
                if plate_text:
                    print(f"✅ PLACA DETECTADA: {plate_text}")
                else:
                    print(f"❌ OCR no pudo leer texto")
            else:
                # HaarCascade no detectó placa
                pass
    except Exception as e:
        print(f"⚠️ Error detectando placa: {e}")
```

---

## 🧪 CÓMO DIAGNOSTICAR

### 1. **Verificar Carga de HaarCascade**

Al iniciar el backend, debes ver:

**✅ CORRECTO**:
```
📦 Cargando HaarCascade para detección de placas...
   Ruta: S:\Construccion\SIMPTV\backend\models\haarcascade_russian_plate_number.xml
   Existe: True
   ✅ Cargado desde archivo local
✅ HaarCascade cargado correctamente para detección de placas
```

**❌ ERROR** (archivo no existe):
```
📦 Cargando HaarCascade para detección de placas...
   Ruta: S:\Construccion\SIMPTV\backend\models\haarcascade_russian_plate_number.xml
   Existe: False
⚠️  HaarCascade local no encontrado, usando OpenCV default
```

**❌ ERROR CRÍTICO** (no se pudo cargar):
```
❌ ERROR CRÍTICO: HaarCascade no pudo cargarse, detección de placas DESHABILITADA
```

---

### 2. **Verificar Detección Durante Video**

Al procesar frames, debes ver:

**✅ PLACA DETECTADA**:
```
🟢 HaarCascade detectó placa: (120, 85, 180, 45) en vehículo 3
📸 Intentando OCR en placa 180x45...
🔍 OCR detectó: 'ABC-1234' (longitud: 8)
🧹 Texto limpio: 'ABC1234' (longitud: 7)
✅ Validación: dígitos=True, letras=True
✅ PLACA VÁLIDA: ABC1234
✅ PLACA DETECTADA: ABC1234
```

**⚠️ NO DETECTA PLACA**:
```
(Sin logs) - HaarCascade no detectó región rectangular
```

**❌ DETECTA PERO OCR FALLA**:
```
🟢 HaarCascade detectó placa: (120, 85, 180, 45) en vehículo 3
📸 Intentando OCR en placa 180x45...
❌ OCR no detectó texto válido
```

---

## 🔧 POSIBLES CAUSAS Y SOLUCIONES

### Causa 1: **HaarCascade no se cargó**

**Síntoma**:
```
❌ ERROR CRÍTICO: HaarCascade no pudo cargarse
```

**Solución**:
```bash
cd backend/models
python download_haarcascade.py
```

Verificar que exista:
```
backend/models/haarcascade_russian_plate_number.xml (73.7 KB)
```

---

### Causa 2: **Vehículo muy pequeño**

**Síntoma**: Vehículos detectados pero sin logs de placas

**Problema**: Si el vehículo ocupa < 100x100 píxeles, la placa será muy pequeña (<25x25)

**Solución**: Ajustar `minSize` en `detect_plate_in_roi()`:

```python
plates = self.plate_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(15, 15)  # 👈 Reducir de (25, 25) a (15, 15)
)
```

---

### Causa 3: **Video de baja calidad**

**Síntoma**: HaarCascade detecta pero OCR falla

**Problema**: Placa borrosa, pixelada, o con mala iluminación

**Solución**: Usar video de mayor resolución (1080p o 4K)

---

### Causa 4: **Placas no rectangulares/visibles**

**Síntoma**: No hay logs de detección

**Problema**: 
- Placa cubierta/sucia
- Ángulo muy inclinado
- Placa no estándar

**Solución**: HaarCascade funciona mejor con:
- Placas frontales/traseras (no laterales)
- Ángulo < 30 grados
- Buena iluminación

---

### Causa 5: **detect_plates=False**

**Síntoma**: No hay logs en absoluto

**Verificar** en `process_frame()`:
```python
result = processor.process_frame(
    frame,
    frame_number,
    detect_plates=True  # 👈 Debe ser True
)
```

---

## 🚀 PASOS PARA PROBAR

### 1. Reiniciar Backend
```bash
cd backend
python manage.py runserver 8001
```

### 2. Verificar Logs de Inicio
Buscar en consola:
```
✅ HaarCascade cargado correctamente para detección de placas
```

### 3. Subir Video desde Frontend
- Video con buena calidad (1080p)
- Vehículos grandes y claros
- Placas visibles

### 4. Observar Logs en Consola
Buscar:
```
🟢 HaarCascade detectó placa: ...
```

### 5. Diagnosticar Resultado

| Logs | Diagnóstico | Acción |
|------|-------------|--------|
| ❌ Sin logs de HaarCascade | No se cargó | Descargar haarcascade |
| ✅ HaarCascade cargado, sin detecciones | Vehículos muy pequeños | Reducir minSize |
| 🟢 Detecta pero ❌ OCR falla | Placa muy pequeña/borrosa | Mejor resolución video |
| ✅ Todo funciona | 🎉 Perfecto | - |

---

## 📊 VERIFICACIÓN RÁPIDA

```bash
# 1. Verificar archivo existe
ls backend/models/haarcascade_russian_plate_number.xml

# 2. Ver logs al iniciar
# Buscar: "✅ HaarCascade cargado"

# 3. Ver logs al procesar
# Buscar: "🟢 HaarCascade detectó placa"
```

---

## 💡 PRÓXIMO PASO

**Prueba ahora con un video y revisa los logs en la consola del backend.**

Si ves:
- ❌ "ERROR CRÍTICO: HaarCascade no pudo cargarse" → Ejecuta `python backend/models/download_haarcascade.py`
- ⚠️ Sin logs de detección → Vehículos muy pequeños, reducir minSize
- ✅ Detecta pero OCR falla → Mejorar preprocesamiento OCR

---

**Generado**: 21/10/2025 23:35
