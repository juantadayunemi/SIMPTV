# Agrupamiento Inteligente de Notificaciones

**Fecha:** Día 2 - Fase de Mejoras  
**Estado:** ✅ **COMPLETADO**  
**Objetivo:** Reducir spam de notificaciones cuando la misma placa es detectada múltiples veces en corto período

---

## 📋 Resumen

Se implementó un sistema de agrupamiento inteligente que detecta cuándo una placa es vista múltiples veces en un período de 5 minutos y agrupa esas detecciones en una sola notificación, evitando el spam.

---

## 🎯 Lógica de Agrupamiento

### Configuración
- **Ventana de tiempo:** 5 minutos
- **Mínimo para agrupar:** 3 detecciones
- **Storage:** Redis Cache (TTL: 6 minutos)

### Flujo de Decisión

```
Detección #1 (0:00) → ✅ ENVIAR notificación normal
Detección #2 (0:30) → 🔇 SILENCIAR (solo 2, mínimo es 3)
Detección #3 (1:00) → ✅ ENVIAR notificación AGRUPADA
Detección #4 (1:30) → 🔇 SILENCIAR (ya notificado)
Detección #5 (2:00) → 🔇 SILENCIAR (ya notificado)
---
Detección #6 (6:00) → ✅ ENVIAR notificación normal (fuera de ventana, resetea)
```

### Ejemplo de Mensajes

**Notificación Normal (1ª detección):**
```
Título: 🚨 Vehiculo con Denuncias Detectado
Cuerpo: Placa PPH4733 tiene 2 denuncia(s). Propietario: Juan Toro
```

**Notificación Agrupada (3ª detección):**
```
Título: 📍 🚨 Placa PPH4733 Detectada Múltiples Veces
Cuerpo: Placa PPH4733 detectada 3 veces en últimos 1 minutos. 2 denuncia(s). Propietario: Juan Toro. Ubicaciones: Cámara Norte, Cámara Sur, Cámara Este
```

---

## 🔧 Implementación Técnica

### 1. **Servicio de Agrupamiento**

**Archivo:** `backend/utils/notification_grouping.py`

```python
class NotificationGroupingService:
    TIME_WINDOW_MINUTES = 5
    MIN_DETECTIONS_TO_GROUP = 3
    CACHE_KEY_PREFIX = "plate_detection"
    CACHE_TTL = 60 * 6  # 6 minutos
    
    @classmethod
    def should_send_notification(
        cls, plate_number, camera_location, complaints_count
    ) -> Tuple[bool, Optional[Dict]]:
        # Retorna:
        #   - bool: True si debe enviar, False si debe silenciar
        #   - Dict: Info de agrupamiento si aplica, None si no
```

**Métodos:**
- `should_send_notification()`: Decide si enviar notificación
- `_save_detection()`: Guarda nueva detección en cache
- `reset_detection()`: Limpia contador (útil para testing)
- `get_detection_stats()`: Obtiene estadísticas (debugging)

**Datos en Cache (Redis):**
```json
{
  "first_detection": "2024-01-05T10:00:00",
  "last_detection": "2024-01-05T10:02:00",
  "count": 3,
  "locations": ["Cámara Norte", "Cámara Sur", "Cámara Este"],
  "complaints_count": 2
}
```

### 2. **Actualización de FCM Service**

**Archivo:** `backend/utils/fcm_service.py`

**Cambios:**
- Nuevo parámetro: `grouping_info: dict | None = None`
- Título y cuerpo dinámicos según agrupamiento
- Payload incluye datos de agrupamiento

```python
def send_vehicle_complaint_alert(
    admin_tokens, plate_number, owner_name, complaints_count,
    severity, camera_location, detection_time, case_number="N/A",
    grouping_info=None  # ✨ NUEVO
):
    if grouping_info and grouping_info.get("is_grouped"):
        title = f"📍 {emoji} Placa {plate_number} Detectada Múltiples Veces"
        body = f"...detectada {detection_count} veces en últimos {time_window}..."
```

**Payload FCM con Agrupamiento:**
```python
data = {
    "type": "vehicle_complaint",
    "plate_number": str(plate_number),
    # ...otros campos...
    "sound": sound,
    "is_grouped": str(grouping_info is not None),
    "detection_count": str(grouping_info.get("detection_count", 1)),
    "time_window_minutes": str(grouping_info.get("time_window_minutes", 0)),
    "locations": ",".join(grouping_info.get("locations", [])),
}
```

### 3. **Integración en Task de Análisis**

**Archivo:** `backend/apps/traffic_app/tasks.py`

**Ubicación:** Antes de enviar FCM (línea ~1177)

```python
# 🆕 VERIFICAR AGRUPAMIENTO INTELIGENTE
from utils.notification_grouping import NotificationGroupingService

should_send, grouping_info = NotificationGroupingService.should_send_notification(
    plate_number=plate_number,
    camera_location=camera_location,
    complaints_count=complaint_detection.totalComplaintsCount
)

if not should_send:
    # Silenciar notificación
    complaint_detection.wasNotified = True
    complaint_detection.notifiedAt = timezone.now()
    complaint_detection.save(update_fields=['wasNotified', 'notifiedAt'])
    return

# Enviar con información de agrupamiento
fcm_result = FCMService.send_vehicle_complaint_alert(
    # ...parámetros...
    grouping_info=grouping_info,  # ✨ NUEVO
)
```

### 4. **Actualización de NotificationLog**

**Cambios en Logging:**
- Título y cuerpo dinámicos según agrupamiento
- Datos adicionales en el log

```python
if grouping_info and grouping_info.get("is_grouped"):
    log_title = f"📍 🚨 Placa {plate_number} Detectada Múltiples Veces"
    log_body = f"...{detection_count} veces en últimos {time_window}..."
    log_data.update({
        "is_grouped": True,
        "detection_count": grouping_info["detection_count"],
        "time_window_minutes": grouping_info["time_window_minutes"],
        "locations": ", ".join(grouping_info.get("locations", [])),
    })
```

---

## 🧪 Testing

### Script de Testing

**Archivo:** `backend/test_notification_grouping.py`

**Escenarios Implementados:**
1. **Test 1:** Primera detección → Enviar notificación ✅
2. **Test 2:** Segunda detección → Silenciar 🔇
3. **Test 3:** Tercera detección → Enviar notificación AGRUPADA 📍
4. **Test 4:** Cuarta detección → Silenciar (ya notificado) 🔇
5. **Test 5:** Detección fuera de ventana (>5 min) → Resetear y enviar ✅

**Ejecutar Tests:**
```bash
cd backend
python manage.py shell < test_notification_grouping.py
```

**Salida Esperada:**
```
🧪 TEST 1: Primera detección de placa
✅ RESULTADO: CORRECTO

🧪 TEST 2: Segunda detección (silenciar)
✅ RESULTADO: CORRECTO

🧪 TEST 3: Tercera detección (notificación agrupada)
  • Detection count: 3
  • Time window: 0 minutos
  • Locations: ['Cámara 1', 'Cámara 2', 'Cámara 3']
✅ RESULTADO: CORRECTO
```

### Testing Manual

1. **Analizar video con misma placa 5 veces:**
   ```bash
   # Usar video con PPH4733 visible múltiples veces
   ```

2. **Verificar logs:**
   ```python
   # Detección #1
   🔔 [FCM STEP 9.5] 📊 Verificando agrupamiento...
   🆕 [GROUPING] Primera detección de PPH4733 - Enviando notificación
   
   # Detección #2
   📊 [GROUPING] PPH4733: 2 detecciones en 0.5min
   🔇 [GROUPING] PPH4733: Solo 2 detecciones - Silenciando notificación
   
   # Detección #3
   📊 [GROUPING] PPH4733: 3 detecciones en 1.2min
   📢 [FCM] Enviando notificación AGRUPADA: 3 detecciones en 1min
   ```

3. **Verificar notificación recibida:**
   - Título debe incluir "Múltiples Veces"
   - Cuerpo debe mostrar contador: "detectada 3 veces"
   - Payload debe incluir `is_grouped: true`

---

## 📊 Estadísticas y Debugging

### Ver Estado de Cache

```python
from utils.notification_grouping import NotificationGroupingService

# Ver estadísticas de una placa
stats = NotificationGroupingService.get_detection_stats("PPH4733")
print(stats)

# Output:
# {
#   "first_detection": "2024-01-05T10:00:00",
#   "last_detection": "2024-01-05T10:02:30",
#   "count": 5,
#   "locations": ["Cámara Norte", "Cámara Sur", "Cámara Este"],
#   "complaints_count": 2
# }
```

### Resetear Contador (Testing)

```python
# Limpiar cache de una placa
NotificationGroupingService.reset_detection("PPH4733")

# Limpiar todo el cache (Redis)
from django.core.cache import cache
cache.clear()
```

### Logs Relevantes

```python
# Grep en logs
🆕 [GROUPING] Primera detección de XXX
📊 [GROUPING] XXX: N detecciones en Xmin
🔇 [GROUPING] XXX: Solo N detecciones - Silenciando
📢 [FCM] Enviando notificación AGRUPADA: N detecciones
⏰ [GROUPING] XXX fuera de ventana (Xmin) - Reseteando
```

---

## ⚙️ Configuración

### Ajustar Parámetros

**Archivo:** `backend/utils/notification_grouping.py`

```python
class NotificationGroupingService:
    # Cambiar ventana de tiempo (default: 5 minutos)
    TIME_WINDOW_MINUTES = 5
    
    # Cambiar mínimo de detecciones (default: 3)
    MIN_DETECTIONS_TO_GROUP = 3
    
    # Cambiar TTL del cache (default: 6 minutos)
    CACHE_TTL = 60 * 6
```

**Ejemplos de Ajustes:**

| Escenario | TIME_WINDOW | MIN_DETECTIONS | Resultado |
|-----------|-------------|----------------|-----------|
| Más restrictivo | 3 min | 5 | Solo agrupa si ≥5 detecciones en 3 min |
| Más permisivo | 10 min | 2 | Agrupa con ≥2 detecciones en 10 min |
| Sin agrupamiento | - | 999 | Nunca agrupa (envía todas) |

---

## 🎯 Casos de Uso

### Caso 1: Vehículo en movimiento constante
```
10:00 - Cámara Norte → ✅ Notificación normal
10:01 - Cámara Centro → 🔇 Silenciada
10:02 - Cámara Sur → ✅ Notificación agrupada (3 ubicaciones)
10:03 - Cámara Oeste → 🔇 Silenciada
```

### Caso 2: Vehículo estacionado
```
10:00 - Cámara A → ✅ Notificación normal
10:15 - Cámara A → 🔇 Silenciada (2ª detección, mismo lugar)
10:30 - Cámara A → ✅ Notificación agrupada (3 detecciones)
10:45 - Cámara A → 🔇 Silenciada
```

### Caso 3: Múltiples placas diferentes
```
10:00 - ABC123 Cámara Norte → ✅ Notificación normal
10:01 - XYZ789 Cámara Norte → ✅ Notificación normal
10:02 - ABC123 Cámara Sur → 🔇 Silenciada (ABC solo tiene 2)
10:03 - XYZ789 Cámara Sur → 🔇 Silenciada (XYZ solo tiene 2)
10:04 - ABC123 Cámara Este → ✅ Notificación agrupada ABC (3 detecciones)
```

---

## 📈 Beneficios

1. **Reduce Spam:**
   - 5 detecciones de misma placa = 2 notificaciones (vs 5 sin agrupamiento)
   - Reducción ~60% en notificaciones

2. **Información Agregada:**
   - Usuario ve patrón de movimiento ("3 veces en 2 minutos")
   - Lista de ubicaciones visitadas

3. **Rendimiento:**
   - Redis cache es extremadamente rápido (<1ms)
   - No afecta tiempo de análisis de video

4. **Flexible:**
   - Configuración ajustable según necesidades
   - Fácil deshabilitar (MIN_DETECTIONS = 999)

---

## 🔄 Flujo Completo

```
1. Video analysis detecta placa con denuncias
   ↓
2. Guarda DetectedPlate y VehicleComplaintDetection en DB
   ↓
3. NotificationGroupingService verifica cache de Redis
   ↓
4a. Primera detección → Enviar notificación normal
4b. 2ª detección → Silenciar, incrementar contador
4c. 3ª detección → Enviar notificación AGRUPADA
4d. 4+ detecciones → Silenciar (ya notificado)
4e. Fuera de ventana → Resetear y enviar normal
   ↓
5. Si debe enviar:
   - FCMService.send_vehicle_complaint_alert(grouping_info=...)
   - NotificationLog con datos de agrupamiento
   - Marcar wasNotified=True
   ↓
6. Si debe silenciar:
   - Marcar wasNotified=True (sin enviar FCM)
   - Log: "Silenciada por agrupamiento"
```

---

## 🐛 Troubleshooting

### Problema: No está agrupando

**Verificar:**
1. Redis está corriendo: `redis-cli ping` → `PONG`
2. Cache está configurado en Django `settings.py`
3. Logs muestran: `📊 [GROUPING] XXX: N detecciones...`

**Solución:**
```python
# Test manual
from utils.notification_grouping import NotificationGroupingService
stats = NotificationGroupingService.get_detection_stats("PLACA")
print(stats)  # Debe mostrar datos o None
```

### Problema: Siempre silencia después de 1ª

**Causa:** MIN_DETECTIONS_TO_GROUP está en 2 (debería ser 3)

**Solución:**
```python
# En notification_grouping.py
MIN_DETECTIONS_TO_GROUP = 3  # Verificar este valor
```

### Problema: Cache no expira

**Verificar:**
```python
from django.core.cache import cache
cache.set('test_key', 'test_value', 60)
cache.get('test_key')  # Debe retornar 'test_value'

import time
time.sleep(61)
cache.get('test_key')  # Debe retornar None
```

---

## 🚀 Próximas Mejoras

1. **Configuración por Usuario:**
   - Permitir admin activar/desactivar agrupamiento
   - Ajustar ventana de tiempo por usuario

2. **Dashboard de Estadísticas:**
   - Mostrar cuántas notificaciones se silenciaron
   - Gráfico de detecciones por placa

3. **Agrupamiento por Cámara:**
   - Opción: "Solo agrupar si misma cámara"
   - Útil para detectar vehículos estacionados

4. **Umbrales Dinámicos:**
   - Ajustar MIN_DETECTIONS según severidad
   - CRITICAL: 2 detecciones, LOW: 5 detecciones

---

## ✅ Checklist de Implementación

- [x] Crear `NotificationGroupingService` con lógica de agrupamiento
- [x] Integrar con Redis Cache
- [x] Actualizar `send_vehicle_complaint_alert()` para soportar agrupamiento
- [x] Integrar en `tasks.py` antes de enviar FCM
- [x] Actualizar `NotificationLog` para reflejar agrupamiento
- [x] Crear script de testing completo
- [x] Documentar configuración y uso
- [x] Definir logs para debugging
- [ ] Testing end-to-end con video real
- [ ] Verificar reducción de spam en producción

---

**Estado Final:** Sistema de agrupamiento implementado y testeado. Listo para pruebas con videos reales. 📊🔇✅
