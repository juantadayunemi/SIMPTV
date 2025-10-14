# Test de Conectividad API

## Problema Detectado
El frontend muestra "Network Error" al intentar crear una cámara.

## Pasos para Diagnosticar

### 1. Verificar que el backend esté corriendo
```bash
# En PowerShell
cd backend
python manage.py runserver 8001
```

### 2. Probar endpoint de locations manualmente
Abre la consola del navegador (F12) y ejecuta:

```javascript
// Test 1: Verificar conexión básica
fetch('http://localhost:8001/api/traffic/locations/')
  .then(res => res.json())
  .then(data => console.log('✅ Locations:', data))
  .catch(err => console.error('❌ Error:', err));

// Test 2: Crear una location
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
    notes: "Test"
  })
})
.then(res => res.json())
.then(data => console.log('✅ Location creada:', data))
.catch(err => console.error('❌ Error:', err));
```

### 3. Posibles Causas del Error

#### A. Backend no está corriendo en el puerto correcto
```bash
# Verificar procesos en puerto 8001
netstat -ano | findstr :8001
```

#### B. Frontend apuntando a puerto incorrecto
Verificar `frontend/.env`:
```
VITE_API_BASE_URL=http://localhost:8001
VITE_API_URL=http://localhost:8001
```

#### C. Problema de CORS
Si ves errores de CORS en la consola, agregar en `backend/config/settings.py`:
```python
CORS_ALLOW_ALL_ORIGINS = True  # ⚠️ Solo para desarrollo
```

#### D. Problema de permisos (AllowAny)
Verificar en `backend/apps/traffic_app/views.py`:
```python
class LocationViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # Debe estar sin autenticación
```

### 4. Frontend - Consola del Navegador
Abrir DevTools (F12) → Network tab
- Filtrar por "locations"
- Intentar crear cámara nuevamente
- Ver qué request aparece (o no aparece)
- Si aparece en rojo: click para ver detalles del error

### 5. Recargar Frontend
```bash
# A veces el problema es cache del navegador
Ctrl + Shift + R  # Recarga forzada (hard reload)
```

### 6. Revisar si hay error de JavaScript
Abrir DevTools (F12) → Console tab
- Buscar errores en rojo
- Si hay algo como "Cannot read property 'id' of undefined", el problema está en el código frontend

## Solución Rápida

1. **Reiniciar backend**:
```bash
cd backend
python manage.py runserver 8001
```

2. **Reiniciar frontend**:
```bash
cd frontend
npm run dev
```

3. **Limpiar cache del navegador**:
- Ctrl + Shift + Delete
- Borrar "Cached images and files"

4. **Probar nuevamente**

## Si el Problema Persiste

Necesito ver:
1. Screenshot de la consola del navegador (F12 → Console)
2. Screenshot del Network tab cuando intentas crear la cámara
3. Output completo del terminal del backend

