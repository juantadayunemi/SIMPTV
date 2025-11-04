# 🚗 Estado de la Detección de Placas

## 📊 Problema Identificado

### ¿Qué significan los logs de Celery?

```log
[2025-11-04 11:41:00,000: INFO/MainProcess] Scheduler: Sending due task aggregate-prediction-data
```

**Este log NO está relacionado con el guardado de imágenes de placas.**

### Explicación de las tareas:

#### 1. **`aggregate-prediction-data`** ⏰
- **Propósito**: Agrupa datos estadísticos de vehículos
- **Frecuencia**: Cada 1 minuto (configurado en `CELERY_BEAT_SCHEDULE`)
- **Función**: Crea registros en `PredictionSource` con:
  - Conteo de vehículos por cámara
  - Velocidad promedio
  - Datos agrupados en bloques de 10 minutos
- **NO guarda imágenes**: Solo procesa números/estadísticas

#### 2. **`analyze_video_async`** 🎬
- **Propósito**: Procesa videos completos
- **Frecuencia**: Se ejecuta cuando subes un video
- **Función**: Detecta vehículos, calcula velocidades, **Y detecta placas**
- **SÍ guarda imágenes**: Si `ENABLE_PLATE_DETECTION=True`

---

## ❌ Problema Detectado

### La detección de placas estaba **DESACTIVADA** porque:

1. ✅ **Faltaba la variable de entorno** `ENABLE_PLATE_DETECTION` en `.env`
2. ✅ **No estaba configurada** en `settings.py`
3. ⚠️ **Las carpetas de salida no existían**:
   - `media/ROI YOLO/` - Para guardar imágenes de vehículos
   - `media/Placas/` - Para guardar imágenes de placas detectadas
   - `media/datos/` - Para guardar JSON con resultados

---

## ✅ Solución Implementada

### 1. Configuración agregada en `.env`:

```env
# Plate Detection Configuration
ENABLE_PLATE_DETECTION=True

# Roboflow API (opcional - mejora la detección con IA)
# ROBOFLOW_API_KEY=your_api_key_here
# ROBOFLOW_PLATE_MODEL=license-plate-recognition-rxg4e/4
```

### 2. Configuración agregada en `settings.py`:

```python
# Plate Detection Configuration
ENABLE_PLATE_DETECTION = config("ENABLE_PLATE_DETECTION", default=False, cast=bool)
ROBOFLOW_API_KEY = config("ROBOFLOW_API_KEY", default=None)
ROBOFLOW_PLATE_MODEL = config("ROBOFLOW_PLATE_MODEL", default="license-plate-recognition-rxg4e/4")
```

---

## 🔄 Cómo Funciona Ahora

### Flujo de detección de placas:

```
Video Subido
    ↓
analyze_video_async (Celery Task)
    ↓
┌─────────────────────────────────────┐
│ Por cada frame (cada 3 frames):    │
│ 1. Detectar vehículos (YOLO)      │
│ 2. Asignar Track IDs               │
│ 3. Calcular velocidades            │
│ 4. Acumular frames para calidad   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Al finalizar el video:              │
│ 1. Analizar mejores frames         │
│ 2. Detectar placas (Triple método) │
│ 3. Validar con OCR                 │
│ 4. Guardar imágenes válidas        │
└─────────────────────────────────────┘
    ↓
Imágenes guardadas en:
- media/ROI YOLO/{video}_analysis_{id}/
- media/Placas/{video}_analysis_{id}/
- media/datos/detections_{video}_analysis_{id}.json
```

---

## 📂 Estructura de Salida

### Carpetas creadas automáticamente:

```
media/
├── ROI YOLO/
│   └── {video_name}_analysis_{analysis_id}/
│       └── {vehicle_id}_{type}_{timestamp}_vehiculo.jpg
│
├── Placas/
│   └── {video_name}_analysis_{analysis_id}/
│       └── {vehicle_id}_{type}_{timestamp}_placa.jpg
│
└── datos/
    └── detections_{video_name}_analysis_{analysis_id}.json
```

### Ejemplo de JSON generado:

```json
{
  "video_name": "traffic_video_20241104",
  "analysis_id": "12345",
  "detections": [
    {
      "vehicle_id": "vehicle_12345_1_1730733600000",
      "vehicle_type": "car",
      "plate_number": "ABC1234",
      "confidence": 0.89,
      "detection_method": "triple",
      "image_path": "/media/Placas/traffic_video_20241104_analysis_12345/vehicle_12345_1_1730733600000_car_20241104_123456_123456_placa.jpg",
      "timestamp": "2024-11-04T12:34:56.123456"
    }
  ]
}
```

---

## 🚀 Próximos Pasos

### 1. **Reiniciar los servicios** para aplicar cambios:

```powershell
# En terminal de Celery (Ctrl+C para detener, luego):
cd backend
venv\Scripts\activate
celery -A config worker -l INFO

# En otra terminal para Celery Beat:
celery -A config beat -l INFO
```

### 2. **Procesar un video de prueba**:

1. Sube un video desde el frontend
2. Espera a que se complete el análisis
3. Verifica las carpetas:
   - `backend/media/ROI YOLO/`
   - `backend/media/Placas/`
   - `backend/media/datos/`

### 3. **Verificar logs** durante el procesamiento:

Busca estos mensajes en los logs de Celery:

```log
✅ Frame Quality Analyzer initialized
🔍 Processing plates for X tracked vehicles...
✨ Best frame for vehicle X: quality=0.XX
🔔 Plate detected: ABC1234 (quality: 0.XX)
✅ Plate processing complete: X detected, Y captured
```

---

## 🔧 Mejoras Opcionales

### Configurar Roboflow API (Recomendado):

Roboflow mejora la precisión de detección de placas usando IA especializada (85-95% vs 60-70% tradicional).

1. **Crear cuenta gratuita**: https://roboflow.com/
2. **Obtener API Key**: Dashboard → Settings → API
3. **Agregar en `.env`**:
   ```env
   ROBOFLOW_API_KEY=tu_api_key_aqui
   ```
4. **Reiniciar servicios**

---

## 📊 Monitoreo

### Verificar estado de detección de placas:

```python
# En Django shell
python manage.py shell

from django.conf import settings
print(f"Plate Detection Enabled: {settings.ENABLE_PLATE_DETECTION}")
print(f"Roboflow API: {'Configured' if settings.ROBOFLOW_API_KEY else 'Not configured'}")
```

### Ver estadísticas de un análisis:

```python
from apps.traffic_app.models import TrafficAnalysis

analysis = TrafficAnalysis.objects.latest('id')
print(f"Analysis ID: {analysis.id}")
print(f"Total Vehicles: {analysis.totalVehicles}")
print(f"Plates Detected: {analysis.platesDetected}")
print(f"Plates Captured: {analysis.platesCaptured}")
```

---

## ⚠️ Notas Importantes

1. **La detección de placas NO afecta el análisis principal**:
   - Si falla la detección, el video se procesa normalmente
   - Los vehículos se guardan sin placa si no se detecta

2. **Requiere EasyOCR**:
   ```bash
   pip install easyocr
   ```
   - Se usa GPU automáticamente si está disponible
   - Fallback a CPU si no hay GPU

3. **Rendimiento**:
   - La detección agrega ~2-5 segundos por vehículo
   - Se procesa DESPUÉS del análisis de video (no bloquea)
   - Solo se procesan los mejores frames (optimizado)

---

## 📝 Resumen

| Aspecto | Antes | Después |
|---------|-------|---------|
| **Detección de placas** | ❌ Desactivada | ✅ Activada |
| **Carpetas de salida** | ❌ No existen | ✅ Se crean automáticamente |
| **Configuración** | ❌ Faltante | ✅ Agregada en .env y settings.py |
| **Logs de Celery** | ⚠️ Confusos (aggregate-prediction-data) | ✅ Clarificados (no relacionado con placas) |
| **Guardado de imágenes** | ❌ No funcionaba | ✅ Funcionará al reiniciar servicios |

---

## 🎯 Conclusión

**El log de `aggregate-prediction-data` que veías NO era un error**, simplemente es una tarea que se ejecuta periódicamente para agrupar estadísticas. **La detección de placas ahora está habilitada** y funcionará en los próximos análisis de video.

**Reinicia los servicios de Celery y procesa un video para ver los resultados.** 🚀
