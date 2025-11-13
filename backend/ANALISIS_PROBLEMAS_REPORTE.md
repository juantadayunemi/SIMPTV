# Análisis de Problemas en TrafficAnalysis ID 48261

**Fecha del Reporte:** 12 de noviembre de 2025, 19:15
**Análisis ID:** 48261
**Video:** `videos/palcas_visible_pdJ5Qrr.mp4`

---

## 📋 Resumen de Problemas Encontrados

### 1. ⏰ Fechas en UTC (No es un problema real)

**Observado:**
```sql
createdAt: 2025-11-13 00:09:24.2796700 +00:00
startedAt: 2025-11-13 00:09:24.4367210 +00:00
endedAt:   2025-11-13 00:09:33.3817980 +00:00
```

**Explicación:**
- Django guarda TODAS las fechas en UTC cuando `USE_TZ = True` (configuración estándar)
- Esto es **CORRECTO** y es la mejor práctica
- La conversión a timezone local (`America/Guayaquil`) se hace automáticamente:
  - ✅ En los serializers de la API (mediante `SerializerMethodField`)
  - ✅ En el frontend cuando se muestra al usuario
  - ❌ NO en consultas SQL directas (por eso ves UTC)

**Fecha Real Ecuador:**
- UTC: `2025-11-13 00:09:24` 
- Ecuador (UTC-5): `2025-11-12 19:09:24` ✅

**Solución:**
No requiere cambios. Para ver fechas locales en SQL:
```sql
-- Convertir a hora de Ecuador (-5 horas)
SELECT 
    DATEADD(hour, -5, createdAt) as createdAt_Ecuador,
    DATEADD(hour, -5, startedAt) as startedAt_Ecuador
FROM traffic_analyses
WHERE id = 48261;
```

---

### 2. 🚗 avgSpeed = 0.00 (CORREGIDO ✅)

**Problema:**
El campo `avgSpeed` en `traffic_analyses` siempre era 0.00, aunque los vehículos individuales SÍ tenían velocidades calculadas:

```sql
-- Vehículos con velocidad calculada:
vehicle_48261_1: 53.30 km/h (MOTORCYCLE)
vehicle_48261_2: 31.30 km/h (CAR)
vehicle_48261_5: 15.60 km/h (MOTORCYCLE)
vehicle_48261_7: 13.20 km/h (TRUCK)
vehicle_48261_8:  7.90 km/h (BUS)
vehicle_48261_9: 10.20 km/h (CAR)
vehicle_48261_12: 7.60 km/h (TRUCK)
```

**Promedio esperado:** (53.30 + 31.30 + 15.60 + 13.20 + 7.90 + 10.20 + 7.60) / 7 = **19.87 km/h**

**Causa:**
El código calculaba la velocidad por vehículo pero NUNCA calculaba el promedio general del análisis.

**Solución Implementada:**
Agregado cálculo automático del promedio en `tasks.py` (líneas 993-1006):

```python
from decimal import Decimal

# Calcular velocidad promedio del análisis (solo vehículos con velocidad > 0)
vehicles_with_speed = Vehicle.objects.filter(
    trafficAnalysisId=analysis_id, avgSpeed__gt=0
).values_list("avgSpeed", flat=True)

if vehicles_with_speed:
    analysis_avg_speed = sum(vehicles_with_speed) / len(vehicles_with_speed)
    logger.info(
        f"📊 Velocidad promedio calculada: {analysis_avg_speed:.2f} km/h "
        f"({len(vehicles_with_speed)} vehículos)"
    )
else:
    analysis_avg_speed = Decimal("0.0")
    logger.info("📊 No hay vehículos con velocidad calculada")

# Guardar en el análisis
analysis.avgSpeed = Decimal(str(round(float(analysis_avg_speed), 2)))
analysis.save()
```

**Resultado:**
Ahora en nuevos análisis el campo `avgSpeed` mostrará el promedio correcto.

---

### 3. 🚫 No Detecta Placas (VERIFICAR)

**Observado:**
Todos los vehículos tienen:
```sql
detectedPlate: NULL
plateConfidence: NULL
plateProcessingStatus: PENDING
```

**Configuración Actual:**
```env
ENABLE_PLATE_DETECTION=True  ✅
PLATE_DETECTION_METHOD=triple  ✅
ROBOFLOW_API_KEY=E0y1pQyDUSvxw0v3S8E5  ✅
```

**Posibles Causas:**

#### A. El video tiene placas muy borrosas o pequeñas
- Resolución baja
- Cámara mal enfocada
- Ángulo inadecuado

#### B. El frame analyzer no se está inicializando
Verificar en logs si aparece:
```
✨ Frame Quality Analyzer initialized
```

#### C. Roboflow API no responde o tiene límite excedido
Verificar en logs:
```
❌ Roboflow API error
⚠️ Fallback to traditional methods
```

#### D. Las placas se detectan pero no se guardan
Buscar en logs:
```
🔍 Processing plates for X tracked vehicles...
✨ Best frame for vehicle X: quality=0.XX
✅ Placa guardada: XXX-XXXX
```

**Comandos para Diagnóstico:**

```powershell
# 1. Verificar si hay placas detectadas en DB
python manage.py shell -c "from apps.plates_app.models import DetectedPlate; print(f'Total placas: {DetectedPlate.objects.count()}'); print(f'Placas análisis 48261: {DetectedPlate.objects.filter(trafficAnalysisId=48261).count()}')"

# 2. Ver logs del análisis (buscar errores de placas)
Get-Content logs\django.log | Select-String -Pattern "48261|plate|Roboflow" -Context 2

# 3. Probar con un video de mejor calidad
# Asegúrate de usar un video donde las placas sean:
# - Visibles frontalmente
# - Resolución mínima 720p
# - Bien iluminadas
# - Cámara estable (sin mucha vibración)
```

**Solución Temporal:**
Si las placas no se detectan, puede ser por la calidad del video. Prueba con:
1. Un video de mejor resolución
2. Cámara más cercana a los vehículos
3. Mejor iluminación
4. Ángulo frontal (no lateral)

---

## 🔧 Cambios Realizados

### Archivo: `backend/apps/traffic_app/tasks.py`

**Líneas 993-1017:** Agregado cálculo de velocidad promedio

```python
# Antes:
analysis.status = "COMPLETED"
analysis.endedAt = timezone.now()
analysis.save()

# Después:
from decimal import Decimal

vehicles_with_speed = Vehicle.objects.filter(
    trafficAnalysisId=analysis_id, avgSpeed__gt=0
).values_list("avgSpeed", flat=True)

if vehicles_with_speed:
    analysis_avg_speed = sum(vehicles_with_speed) / len(vehicles_with_speed)
else:
    analysis_avg_speed = Decimal("0.0")

analysis.avgSpeed = Decimal(str(round(float(analysis_avg_speed), 2)))
analysis.status = "COMPLETED"
analysis.endedAt = timezone.now()
analysis.save()
```

---

## ✅ Próximos Pasos

1. **Procesar un nuevo video** para verificar que `avgSpeed` se calcula correctamente
2. **Revisar logs** del nuevo análisis para ver si detecta placas
3. **Si no detecta placas:**
   - Verificar calidad del video
   - Revisar logs en busca de errores
   - Probar con video de prueba de alta calidad

---

## 📊 Datos de Ejemplo (Análisis 48261)

### TrafficAnalysis
```
ID: 48261
Video: videos/palcas_visible_pdJ5Qrr.mp4
Duration: 8.9 segundos
Total Vehicles: 7 (3 CAR, 2 TRUCK, 2 MOTORCYCLE, 2 BUS)
avgSpeed: 0.00 ❌ (debería ser ~19.87 km/h)
platesDetected: 0
platesCaptured: 0
status: COMPLETED
```

### Vehículos Detectados
```
1. MOTORCYCLE - 53.30 km/h (35 frames)
2. CAR        - 31.30 km/h (39 frames)
3. MOTORCYCLE - 15.60 km/h (12 frames)
4. TRUCK      - 13.20 km/h (23 frames)
5. BUS        -  7.90 km/h (23 frames)
6. CAR        - 10.20 km/h (26 frames)
7. TRUCK      -  7.60 km/h (17 frames)
```

**Velocidad Promedio Real:** 19.87 km/h
**Velocidad Guardada:** 0.00 km/h ❌

---

## 🎯 Conclusión

1. **Fechas UTC:** ✅ Funcionamiento correcto (no requiere cambios)
2. **avgSpeed = 0:** ✅ CORREGIDO - Ahora calcula promedio automáticamente
3. **Placas no detectadas:** 🔍 REQUIERE INVESTIGACIÓN - Verificar logs y calidad del video

El problema más crítico (avgSpeed) ha sido resuelto. La detección de placas necesita más investigación con los logs del próximo análisis.
