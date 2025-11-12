# 🚀 Guía Rápida - Probar Cámara IP

## ✅ Checklist Previo

### En tu Celular:
- [ ] App **IP Webcam** instalada
- [ ] Presionaste **"Start server"** (al final de la app)
- [ ] La app muestra: `http://192.168.1.3:8080`
- [ ] Celular y PC en la **misma red WiFi**

### En tu PC:
- [ ] Frontend corriendo (`npm run dev` en `frontend/`)
- [ ] Backend corriendo (Django server)

## 🧪 Prueba Rápida de Conexión

### Opción 1: Desde el Navegador
Abre en tu navegador:
```
http://192.168.1.3:8080/video
```

**Debes ver:** El video de tu cámara en el navegador
- ✅ Si funciona → La cámara está lista
- ❌ Si no funciona → Verifica WiFi y que la app esté en "Start server"

### Opción 2: Desde la App
1. Ve a `http://localhost:5173/monitoring/live`
2. En el dropdown de cámaras, busca: **📱 Cámara IP - Celular (IP Webcam)**
3. Selecciónala
4. Click en **"Iniciar"**

**Debes ver:**
- ✅ Video en vivo desde tu celular
- ✅ Detecciones YOLO con cajas (si hay vehículos)
- ✅ Indicador "TRANSMITIENDO" en rojo

## ❌ Solución de Problemas

### Error: "No se pudo conectar a la cámara IP"

**Causas comunes:**

1. **IP Webcam no está en "Start server"**
   - Solución: Abre la app y presiona "Start server"

2. **IP incorrecta**
   - Verifica en la app la IP actual
   - Si cambió, edita: `frontend/src/pages/monitoring/LiveMonitoring.tsx` línea ~155

3. **Diferentes redes WiFi**
   - Conecta celular y PC a la **misma red WiFi**

4. **Firewall bloqueando**
   - Windows: Desactiva temporalmente el firewall
   - O permite el puerto 8080

### Error: "El video se carga pero no se ve"

**Solución:**
1. Abre las **DevTools** del navegador (F12)
2. Ve a la pestaña **Console**
3. Busca mensajes de error
4. Copia y pégame los errores

### Error: "CORS policy" en consola

**Solución:**
IP Webcam tiene una configuración para permitir CORS:
1. En la app, ve a **"Connection settings"**
2. Busca **"CORS requests"**
3. Actívalo

## 📊 Rendimiento Esperado

- **FPS del video:** 15-30 (depende de tu WiFi)
- **FPS de YOLO:** ~3 (procesamiento cada 300ms)
- **Latencia:** 200-500ms (normal en WiFi)

## 🎯 Qué Debes Ver

```
┌─────────────────────────────────┐
│  📱 Cámara IP - Celular         │  ← Dropdown
└─────────────────────────────────┘
┌─────────────────────────────────┐
│                                 │
│    [Video en vivo]              │  ← Video de tu celular
│    Con cajas de detección       │
│                                 │
└─────────────────────────────────┘
┌───────┐ ┌───────┐ ┌────────────┐
│Iniciar│ │Detener│ │Grabar/Guar.│  ← Botones
└───────┘ └───────┘ └────────────┘
```

## 🔍 Verificar Conexión Manualmente

### Método 1: curl (PowerShell)
```powershell
curl http://192.168.1.3:8080/video
```

Si funciona, verás datos binarios (bytes del video)

### Método 2: Navegador
```
http://192.168.1.3:8080
```

Debes ver la interfaz web de IP Webcam

## ✅ Todo Funciona - Siguiente Paso

Una vez que veas el video:
1. **Prueba YOLO:** Apunta la cámara a un auto/moto
2. **Verás cajas** alrededor de los vehículos detectados
3. **Graba:** Click en "Grabar" para guardar el video
4. **Detén y guarda:** Click de nuevo para subir a S3

## 📞 Necesitas Ayuda

Si sigues teniendo problemas, dame:
1. Screenshot de la consola del navegador (F12)
2. Screenshot de IP Webcam app mostrando la IP
3. Resultado de abrir `http://192.168.1.3:8080` en el navegador

---

**Fecha:** 10 de Noviembre, 2025
**Tu IP configurada:** `http://192.168.1.3:8080`
