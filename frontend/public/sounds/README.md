# Sonidos de Notificaciones TrafiSmart

## Archivos de Audio Requeridos

Esta carpeta debe contener los siguientes archivos de audio para las notificaciones según severidad:

### 1. `default.mp3` (Severidad: NONE, LOW)
- **Uso**: Notificaciones generales o de baja prioridad
- **Características**: Sonido suave y no intrusivo
- **Duración recomendada**: 1-2 segundos
- **Ejemplo**: Tono de notificación estándar

### 2. `alert.mp3` (Severidad: MEDIUM)
- **Uso**: Vehículos con 3-4 denuncias
- **Características**: Sonido de atención moderada
- **Duración recomendada**: 2-3 segundos
- **Ejemplo**: Doble beep o tono de alerta

### 3. `urgent.mp3` (Severidad: HIGH)
- **Uso**: Vehículos con 5-6 denuncias
- **Características**: Sonido urgente y llamativo
- **Duración recomendada**: 3-4 segundos
- **Ejemplo**: Triple beep rápido o alarma moderada

### 4. `alarm.mp3` (Severidad: CRITICAL)
- **Uso**: Vehículos con 7 o más denuncias
- **Características**: Sonido de alarma crítica
- **Duración recomendada**: 4-5 segundos
- **Ejemplo**: Sirena o alarma continua

## Cómo Obtener/Crear los Sonidos

### Opción 1: Usar Sonidos del Sistema
Puedes copiar sonidos de tu sistema Windows:
- `C:\Windows\Media\` - Carpeta con sonidos del sistema

### Opción 2: Descargar de Sitios Gratuitos
- [Freesound.org](https://freesound.org/) - Busca: "notification", "alert", "alarm"
- [Zapsplat.com](https://www.zapsplat.com/) - Sonidos gratuitos
- [Mixkit.co](https://mixkit.co/free-sound-effects/alarm/) - Efectos de sonido

### Opción 3: Generar con Web Audio API
Ver `sound-generator.html` en esta carpeta para generar tonos sintéticos

## Formatos Soportados

Los navegadores modernos soportan:
- **MP3** (recomendado para compatibilidad)
- **OGG** (alternativa open-source)
- **WAV** (mayor calidad pero mayor tamaño)

## Implementación

El sistema de sonidos está configurado en:
1. **Backend**: `backend/utils/fcm_service.py` - Define qué sonido enviar según severidad
2. **Service Worker**: `frontend/public/firebase-messaging-sw.js` - Mapea sonidos a archivos
3. **Vibración**: Patrones personalizados según severidad en dispositivos móviles

## Patrones de Vibración Actuales

```javascript
{
  'default': [200, 100, 200],           // Dos vibraciones cortas
  'alert': [300, 100, 300, 100, 300],   // Tres vibraciones medianas
  'urgent': [500, 100, 500, 100, 500, 100, 500], // Cuatro vibraciones largas
  'alarm': [700, 100, 700, 100, 700, 100, 700, 100, 700] // Cinco vibraciones muy largas
}
```

## Testing

Para probar los sonidos después de agregarlos:
1. Agregar los archivos MP3 en esta carpeta
2. Reiniciar el frontend: `npm run dev`
3. Analizar un video con vehículo que tenga denuncias
4. Verificar que se reproduzca el sonido correcto según la severidad

## Notas Importantes

⚠️ **Limitaciones de Service Workers**:
- Los Service Workers tienen restricciones para reproducir audio
- La propiedad `sound` en notificaciones es experimental
- La vibración funciona principalmente en dispositivos móviles
- Chrome/Edge en Windows pueden no reproducir audio personalizado de Service Workers

✅ **Alternativa Implementada**:
- Patrones de vibración personalizados según severidad
- Tag único para evitar deduplicación
- `requireInteraction: true` para notificaciones persistentes
- Información de sonido guardada en `data.soundUrl` para uso futuro

## Próximas Mejoras

- [ ] Implementar reproducción de audio en el frontend cuando la notificación se muestre (fuera del SW)
- [ ] Agregar configuración de usuario para activar/desactivar sonidos
- [ ] Permitir al usuario seleccionar sonidos personalizados
- [ ] Implementar volumen ajustable por severidad
