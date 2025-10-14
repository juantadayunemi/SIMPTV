# 🔧 Solución: Network Error al Crear Cámara

## Problema
Al intentar crear una nueva cámara aparece "Network Error" y no se puede guardar.

## Causa Identificada
El backend está corriendo en el puerto 8001 pero puede haber problemas de:
1. Frontend no llega a enviar la petición
2. Error de JavaScript antes de hacer la petición
3. Backend no responde correctamente

## Solución Paso a Paso

### 1. Verificar que el Backend esté Corriendo
```bash
# Terminal 1: Backend
cd backend
python manage.py runserver 8001
```

Deberías ver:
```
Starting ASGI/Daphne version 4.1.2 development server at http://127.0.0.1:8001/
```

### 2. Verificar que el Frontend esté Corriendo
```bash
# Terminal 2: Frontend
cd frontend
npm run dev
```

Deberías ver:
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5174/
```

### 3. Abrir la Consola del Navegador
1. Presiona `F12` o `Ctrl + Shift + I`
2. Ve a la pestaña "Console"
3. Ve a la pestaña "Network"
4. Intenta crear una cámara nuevamente

### 4. Revisar Errores en la Consola

#### Si ves errores en rojo:
```
❌ Uncaught TypeError: Cannot read property 'id' of undefined
```
**Solución**: El problema está en el código frontend

#### Si ves errores de CORS:
```
❌ Access to fetch at 'http://localhost:8001/api/traffic/locations/' has been blocked by CORS
```
**Solución**: Agregar origen en `backend/config/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5174",  # ← Verificar que esté este
]
```

#### Si NO ves ninguna petición en Network tab:
El frontend no está llegando a hacer la petición. Probablemente hay un error de validación.

### 5. Test Manual de la API

Abre la consola del navegador (F12 → Console) y ejecuta:

```javascript
// Test 1: Crear una location
fetch('http://localhost:8001/api/traffic/locations/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    description: "Test Location",
    latitude: -0.1807,
    longitude: -78.4678,
    city: "Quito",
    province: "Pichincha",
    country: "Ecuador",
    notes: "Test desde consola"
  })
})
.then(res => {
  console.log('Status:', res.status);
  return res.json();
})
.then(data => console.log('✅ Location creada:', data))
.catch(err => console.error('❌ Error:', err));
```

Si funciona, verás:
```
✅ Location creada: {id: 3, description: "Test Location", ...}
```

### 6. Solución Temporal: Deshabilitar Autenticación

Si el problema es de autenticación, temporalmente:

**backend/apps/traffic_app/views.py**:
```python
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]  # ← Verificar que esté sin autenticación

class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    permission_classes = [AllowAny]  # ← Verificar que esté sin autenticación
```

### 7. Revisar Variables de Entorno

**frontend/.env**:
```env
VITE_API_BASE_URL=http://localhost:8001
VITE_API_URL=http://localhost:8001
VITE_WS_URL=localhost:8001
```

### 8. Hard Reload del Navegador

A veces el cache del navegador causa problemas:
- `Ctrl + Shift + R` (Windows/Linux)
- `Cmd + Shift + R` (Mac)

O limpia el cache:
- `Ctrl + Shift + Delete`
- Selecciona "Cached images and files"
- Click "Clear data"

### 9. Reiniciar Todo

```bash
# 1. Cerrar backend (Ctrl + C)
# 2. Cerrar frontend (Ctrl + C)

# 3. Reiniciar backend
cd backend
python manage.py runserver 8001

# 4. Reiniciar frontend (en otra terminal)
cd frontend
npm run dev

# 5. Abrir navegador en modo incógnito
# Presiona Ctrl + Shift + N (Chrome) o Ctrl + Shift + P (Firefox)
# Ve a http://localhost:5174
```

## Debugging Avanzado

### Verificar el payload que se envía

Abre **frontend/src/pages/traffic/CamerasPage.tsx** y agrega logs:

```tsx
const handleAddCamera = async (cameraData: CameraFormData) => {
  try {
    console.log('📸 Creating camera:', cameraData);
    
    // 1. Crear la ubicación
    console.log('🌍 Creando location...');
    const locationPayload = {
      description: cameraData.locationDescription,
      latitude: cameraData.latitude,
      longitude: cameraData.longitude,
      city: cameraData.city,
      province: cameraData.province,
      country: cameraData.country,
      notes: `Ubicación creada para cámara: ${cameraData.name}`,
    };
    console.log('📤 Location payload:', locationPayload);
    
    const location = await trafficService.createLocation(locationPayload);
    console.log('✅ Location created:', location);
    
    // ... resto del código
```

### Verificar requests en el backend

Los logs del backend deberían mostrar:
```
INFO HTTP OPTIONS /api/traffic/locations/ 200
INFO HTTP POST /api/traffic/locations/ 201  ← Esto debe aparecer
```

Si ves:
```
WARNING HTTP POST /api/traffic/locations/ 400  ← Error de validación
```

Significa que falta un campo requerido o hay datos inválidos.

## Solución Final Probada

Si todo lo anterior falla, usa este código probado:

**Test directo en la consola del navegador**:
```javascript
// Paso 1: Crear location
const locationData = {
  description: "Calle Pedro Menéndez Gilbert, Durán",
  latitude: -2.1704,
  longitude: -79.8352,
  city: "Durán",
  province: "Guayas",
  country: "Ecuador",
  notes: "Test"
};

fetch('http://localhost:8001/api/traffic/locations/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(locationData)
})
.then(res => res.json())
.then(location => {
  console.log('✅ Location ID:', location.id);
  
  // Paso 2: Crear cámara
  const cameraData = {
    name: "Test Camera",
    brand: "ss",
    model: "1",
    resolution: "1920x1080 (Full HD)",
    fps: 30,
    locationId: location.id,  // ← Usar el ID de la location creada
    lanes: 2,
    coversBothDirections: false,
    notes: "2"
  };
  
  return fetch('http://localhost:8001/api/traffic/cameras/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cameraData)
  });
})
.then(res => res.json())
.then(camera => {
  console.log('✅ Camera created:', camera);
})
.catch(err => console.error('❌ Error:', err));
```

## Próximos Pasos

Una vez que la cámara se cree correctamente:
1. Recargar la página de cámaras
2. Debería aparecer en la lista
3. Ahora puedes subir videos y hacer análisis

Si el problema persiste, por favor comparte:
1. Screenshot de la consola del navegador (F12 → Console)
2. Screenshot de Network tab mostrando las peticiones
3. Logs completos del backend

