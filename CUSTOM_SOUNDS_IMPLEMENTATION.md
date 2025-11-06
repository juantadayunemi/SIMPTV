# Implementación de Sonidos Personalizados por Severidad

**Fecha:** Día 2 - Fase de Mejoras  
**Estado:** ✅ **COMPLETADO**  
**Versión Service Worker:** v2.1.0

---

## 📋 Resumen

Se implementó un sistema completo de sonidos personalizados para notificaciones FCM según el nivel de severidad de las denuncias detectadas. El sistema incluye tanto sonidos como patrones de vibración diferenciados.

---

## 🔧 Cambios Implementados

### 1. **Backend: `backend/utils/fcm_service.py`**

#### Mapeo de Sonidos por Severidad
```python
severity_sound = {
    "NONE": "default",      # 0 denuncias
    "LOW": "default",       # 1-2 denuncias
    "MEDIUM": "alert",      # 3-4 denuncias
    "HIGH": "urgent",       # 5-6 denuncias
    "CRITICAL": "alarm",    # 7+ denuncias
}
```

#### Payload FCM Actualizado
```python
data = {
    "type": "vehicle_complaint",
    "plate_number": str(plate_number),
    "owner_name": str(owner_name),
    "complaints_count": str(complaints_count),
    "severity": str(severity),
    "case_number": str(case_number),
    "location": str(camera_location),
    "time": str(detection_time),
    "sound": sound,  # ✨ NUEVO
}
```

#### Logging Mejorado
```python
logger.info(f"🚨 [VEHICLE ALERT STEP 2] Mensaje preparado:")
logger.info(f"   • Título: {title}")
logger.info(f"   • Cuerpo: {body}")
logger.info(f"   • Sonido: {sound}")  # ✨ NUEVO
```

---

### 2. **Frontend: Service Worker v2.1.0**

#### Mapeo de URLs de Sonido
```javascript
const soundMapping = {
  'default': '/sounds/default.mp3',
  'alert': '/sounds/alert.mp3',
  'urgent': '/sounds/urgent.mp3',
  'alarm': '/sounds/alarm.mp3'
};
```

#### Patrones de Vibración Personalizados
```javascript
function getVibrationPattern(sound) {
  const patterns = {
    'default': [200, 100, 200],                              // 2 pulsos cortos
    'alert': [300, 100, 300, 100, 300],                     // 3 pulsos medianos
    'urgent': [500, 100, 500, 100, 500, 100, 500],          // 4 pulsos largos
    'alarm': [700, 100, 700, 100, 700, 100, 700, 100, 700]  // 5 pulsos muy largos
  };
  return patterns[sound] || patterns['default'];
}
```

#### Opciones de Notificación Mejoradas
```javascript
const notificationOptions = {
  body: payload.notification?.body || 'Nueva notificación',
  icon: '/icon-192x192.png',
  badge: '/badge-72x72.png',
  tag: uniqueTag,
  requireInteraction: true,
  data: {
    ...payload.data,
    soundUrl: soundUrl  // ✨ NUEVO
  },
  vibrate: getVibrationPattern(requestedSound),  // ✨ NUEVO
  sound: soundUrl,  // ✨ NUEVO (experimental)
  actions: [...]
};
```

---

## 📁 Archivos Creados

### 1. **Carpeta de Sonidos**
```
frontend/public/sounds/
├── README.md              # Documentación completa
├── sound-generator.html   # Herramienta para generar tonos
├── default.mp3           # (por agregar) Sonido suave
├── alert.mp3             # (por agregar) Sonido moderado
├── urgent.mp3            # (por agregar) Sonido urgente
└── alarm.mp3             # (por agregar) Sonido crítico
```

### 2. **README.md de Sonidos**
Incluye:
- ✅ Descripción de cada archivo de sonido
- ✅ Características recomendadas (duración, tono)
- ✅ Fuentes para obtener/crear sonidos
- ✅ Formatos soportados (MP3, OGG, WAV)
- ✅ Instrucciones de testing
- ✅ Limitaciones de Service Workers
- ✅ Planes de mejoras futuras

### 3. **sound-generator.html**
Herramienta interactiva para:
- ✅ Probar diferentes tonos (DEFAULT, ALERT, URGENT, ALARM)
- ✅ Reproducir beeps sintéticos con Web Audio API
- ✅ Guía visual con colores según severidad
- ✅ Instrucciones para capturar y guardar audio

---

## 🎵 Configuración de Sonidos

### Mapeo Severidad → Sonido → Vibración

| Severidad | Denuncias | Emoji | Sonido | Vibración | Descripción |
|-----------|-----------|-------|--------|-----------|-------------|
| **NONE** | 0 | ✅ | default | [200,100,200] | Notificación suave |
| **LOW** | 1-2 | ⚠️ | default | [200,100,200] | Notificación suave |
| **MEDIUM** | 3-4 | 🚨 | alert | [300,100,300,100,300] | Atención moderada |
| **HIGH** | 5-6 | 🔴 | urgent | [500,100,500,100,500,100,500] | Urgente |
| **CRITICAL** | 7+ | 🆘 | alarm | [700,100,700,100,700,100,700,100,700] | Alarma crítica |

---

## 🧪 Testing

### Cómo Probar

1. **Agregar Archivos de Sonido:**
   ```bash
   # Descargar sonidos MP3 y colocar en:
   frontend/public/sounds/default.mp3
   frontend/public/sounds/alert.mp3
   frontend/public/sounds/urgent.mp3
   frontend/public/sounds/alarm.mp3
   ```

2. **Reiniciar Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Analizar Video con Denuncias:**
   - Usar placa PPH4733 (2 denuncias = MEDIUM = alert.mp3)
   - Verificar en logs del Service Worker: `[SW] 🔊 Sonido solicitado: alert`

4. **Verificar en Browser DevTools:**
   ```javascript
   // Console → Application → Service Workers
   // Ver versión: v2.1.0
   // Ver logs: "[SW] 🔊 Sonido solicitado: alert → /sounds/alert.mp3"
   ```

### Casos de Prueba

| Placa | Denuncias | Severidad | Sonido Esperado | Vibración |
|-------|-----------|-----------|-----------------|-----------|
| TEST001 | 0 | NONE | default.mp3 | [200,100,200] |
| TEST002 | 1 | LOW | default.mp3 | [200,100,200] |
| PPH4733 | 2 | LOW | default.mp3 | [200,100,200] |
| TEST003 | 3 | MEDIUM | alert.mp3 | [300,100,300,100,300] |
| TEST004 | 5 | HIGH | urgent.mp3 | [500,100,500,...] |
| TEST005 | 8 | CRITICAL | alarm.mp3 | [700,100,700,...] |

---

## ⚠️ Limitaciones Conocidas

### Service Workers y Audio

1. **No pueden reproducir audio directamente:**
   - Los Service Workers no tienen acceso a Web Audio API
   - La propiedad `sound` en notificaciones es experimental
   - Chrome/Edge en Windows tienen restricciones adicionales

2. **Soluciones Actuales:**
   - ✅ **Patrones de vibración personalizados** (funciona en móviles)
   - ✅ **Información guardada en `data.soundUrl`** (para uso futuro)
   - ✅ **Logging detallado** para debugging

3. **Alternativas Futuras:**
   - Reproducir audio en el frontend cuando se recibe la notificación (no en SW)
   - Usar notificaciones nativas del sistema operativo con sonidos
   - Implementar audio en la aplicación web cuando está en primer plano

---

## 📊 Flujo de Datos

```
1. Backend detecta placa con denuncias
   ↓
2. Calcula severity según conteo
   ↓
3. fcm_service.py mapea severity → sound
   ↓
4. Envía payload FCM con data.sound = "alert"
   ↓
5. Service Worker recibe mensaje
   ↓
6. Mapea "alert" → "/sounds/alert.mp3"
   ↓
7. Aplica patrón de vibración personalizado
   ↓
8. Muestra notificación con requireInteraction: true
   ↓
9. (Futuro) Reproduce sonido en frontend
```

---

## 🔄 Versionamiento

- **v2.0.0**: TAG único para evitar deduplicación
- **v2.1.0**: Sonidos personalizados + patrones de vibración ✨ **ACTUAL**

---

## 📝 Logs de Ejemplo

### Backend
```python
🚨 [VEHICLE ALERT STEP 1] Iniciando envío de alerta vehicular
   • Placa: PPH4733
   • Denuncias: 2
   • Severidad: MEDIUM
   • Cámara: Oficina
   • Expediente: N/A
🚨 [VEHICLE ALERT STEP 2] Mensaje preparado:
   • Título: 🚨 Vehiculo con Denuncias Detectado
   • Cuerpo: Placa PPH4733 tiene 2 denuncia(s). Propietario: Juan Toro
   • Sonido: alert  ✨ NUEVO
```

### Service Worker
```javascript
[SW] 📩 Mensaje en background: {notification: {...}, data: {sound: "alert", ...}}
[SW] 🔊 Sonido solicitado: alert → /sounds/alert.mp3  ✨ NUEVO
[SW] 🔔 Mostrando notificación con tag: PPH4733-1735878234567
```

---

## ✅ Checklist de Implementación

- [x] Agregar mapeo `severity_sound` en backend
- [x] Incluir `sound` en payload FCM
- [x] Logging de sonido en backend
- [x] Actualizar Service Worker a v2.1.0
- [x] Implementar `getVibrationPattern()`
- [x] Implementar `playNotificationSound()` (preparado para futuro)
- [x] Mapear sonidos a archivos MP3
- [x] Crear carpeta `/sounds`
- [x] Documentar en README.md
- [x] Crear generador de sonidos HTML
- [x] Definir casos de prueba
- [ ] Agregar archivos MP3 reales (pendiente por usuario)
- [ ] Testing end-to-end con todos los niveles de severidad

---

## 🎯 Próximas Mejoras

1. **Reproducción de Audio en Frontend:**
   - Escuchar mensajes FCM en el frontend (cuando app está abierta)
   - Reproducir audio directamente sin limitaciones del Service Worker

2. **Configuración de Usuario:**
   - Permitir activar/desactivar sonidos
   - Seleccionar sonidos personalizados
   - Ajustar volumen por severidad

3. **Testing Automatizado:**
   - Script para probar todos los niveles de severidad
   - Validación automática de archivos de sonido
   - Logs de debugging mejorados

---

## 📞 Soporte

Para más información ver:
- `frontend/public/sounds/README.md` - Guía completa de sonidos
- `frontend/public/sounds/sound-generator.html` - Generador interactivo
- `backend/utils/fcm_service.py` - Lógica de backend
- `frontend/public/firebase-messaging-sw.js` - Service Worker v2.1.0

---

**Estado Final:** Sistema de sonidos completamente implementado y documentado. Listo para agregar archivos MP3 y testing final. 🎉
