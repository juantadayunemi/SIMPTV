# 🚀 Guía Rápida - DroidCam

## ✅ Pasos para Conectar DroidCam

### 1️⃣ En tu Celular Android:
1. Abre la app **DroidCam**
2. Verás la pantalla principal con la IP: `http://192.168.1.3:4747`
3. ¡Listo! La cámara ya está transmitiendo

**No necesitas presionar nada más** - DroidCam transmite automáticamente

### 2️⃣ Prueba Rápida en Navegador:

Abre en tu navegador:
```
http://192.168.1.3:4747/video
```

**Debes ver:** El video de tu cámara en formato MJPEG
- ✅ Si funciona → Todo listo para usar en la app
- ❌ Si no funciona → Lee troubleshooting abajo

### 3️⃣ Usar en TrafiSmart:

1. Ve a: `http://localhost:5173/monitoring/live`
2. En el dropdown de cámaras, selecciona: **📱 DroidCam - Celular**
3. Click en **"Iniciar"**
4. ✅ Deberías ver el video con detecciones YOLO

## 🔧 Configuración de DroidCam (Opcional)

Para mejor calidad, en la app:
- **Video Settings**
  - Resolution: 640x480 (bueno) o 1280x720 (mejor calidad)
  - FPS: 30
  - Quality: High

## ❌ Troubleshooting

### Problema: No se ve el video en navegador

**Solución 1: Verifica WiFi**
```powershell
# En PowerShell, verifica que puedes hacer ping
ping 192.168.1.3
```
Debe responder. Si no responde, están en redes diferentes.

**Solución 2: Verifica que DroidCam esté abierta**
- La app debe estar en primer plano
- No debe estar en modo "pause" o bloqueada

**Solución 3: Reinicia DroidCam**
- Cierra la app completamente
- Ábrela de nuevo
- Verifica la IP (puede cambiar)

### Problema: La IP cambió

Si tu celular tiene otra IP (ejemplo: `192.168.1.5`), actualiza aquí:

**Frontend:** `frontend/src/pages/monitoring/LiveMonitoring.tsx` (línea ~155)
```typescript
ipUrl: 'http://192.168.1.5:4747/video'  // Nueva IP
```

**Backend:** `backend/config/ip_cameras.py` (línea ~12)
```python
"url": "http://192.168.1.5:4747/video",  # Nueva IP
```

### Problema: "Connection refused" o "ERR_CONNECTION_REFUSED"

**Causas:**
1. **Firewall en el celular** - Desactívalo temporalmente
2. **Puerto bloqueado** - DroidCam usa puerto 4747
3. **Red pública** - Algunas redes WiFi públicas bloquean esto

**Solución:**
- Usa tu propia red WiFi en casa
- O crea un hotspot desde el celular y conéctate desde PC

## 🧪 Test Backend (Opcional)

Si instalaste opencv-python:
```bash
cd backend
python test_ip_webcam.py
```

Esto probará:
- ✅ Conexión a DroidCam
- ✅ Captura de frames
- ✅ Detección YOLO

## 📊 URLs de DroidCam

DroidCam proporciona:
- **Video stream:** `http://192.168.1.3:4747/video` ✅ Usamos esta
- **Snapshot:** `http://192.168.1.3:4747/shot.jpg`
- **Interface web:** `http://192.168.1.3:4747`

## ✅ Ventajas de DroidCam

- ✅ Más estable que IP Webcam
- ✅ Menor latencia
- ✅ Mejor compatibilidad con MJPEG
- ✅ Transmite automáticamente (no necesitas Start Server)
- ✅ Interfaz más simple

## 🎯 Siguiente Paso

Una vez funcionando:
1. **Apunta la cámara a un vehículo**
2. **Verás las cajas de detección** alrededor
3. **Click en "Grabar"** para guardar
4. **Click de nuevo** para detener y subir a S3

---

**Tu IP:** `http://192.168.1.3:4747`
**Puerto:** 4747
**App:** DroidCam

**Fecha:** 10 de Noviembre, 2025
