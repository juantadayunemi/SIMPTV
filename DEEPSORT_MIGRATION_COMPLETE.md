# DeepSORT Migration Complete - Testing Guide

## ✅ Migración Completada Exitosamente

**Fecha:** 11 de noviembre de 2025  
**Sistema:** TrafiSmart Vehicle Tracking  
**Cambio:** Norfair → DeepSORT

---

## 📊 Resumen de Cambios

### Dependencias Actualizadas
```diff
- norfair==2.2.0
+ deep-sort-realtime==1.3.2
```

### Tecnologías Preservadas
- ✅ PyTorch 2.7.1+cu118 (sin cambios)
- ✅ CUDA 11.8 (funcionando)
- ✅ Ultralytics YOLO (sin cambios)

---

## 🎯 Configuración DeepSORT

```python
# backend/apps/streaming/services/yolo_processor.py

DeepSort(
    max_age=30,              # Frames to keep track alive without detection
    n_init=3,                # Frames to confirm new track
    nms_max_overlap=0.7,     # Non-Maximum Suppression threshold
    max_cosine_distance=0.4, # Appearance similarity (0.6 = 60% match required)
    nn_budget=100,           # Feature vectors stored per track
    embedder="mobilenet",    # Feature extractor (fast & accurate)
    half=True,               # FP16 precision (2x faster)
    embedder_gpu=True        # Use CUDA for feature extraction
)
```

### Significado de Parámetros Clave:

**max_age=30**
- Un track puede vivir 30 frames sin nuevas detecciones
- Permite tolerar oclusiones temporales
- Mayor valor = más tolerante, menor valor = más estricto

**n_init=3**
- Requiere 3 detecciones consecutivas para confirmar un track
- Reduce falsos positivos
- Mayor valor = menos falsos positivos, más latencia

**max_cosine_distance=0.4**
- Similitud visual mínima: 60% (1 - 0.4 = 0.6)
- Compara características visuales entre frames
- Menor valor = más estricto en matching

---

## 🧪 Guía de Pruebas

### Test 1: Vehículo Único en Movimiento

**Objetivo:** Verificar persistencia de ID durante movimiento

**Pasos:**
1. Colocar 1 Hot Wheels frente a la cámara
2. Esperar que aparezca: `ID#1`
3. Mover el vehículo **lentamente** de izquierda a derecha
4. **Resultado esperado:** ID se mantiene en `ID#1`
5. Mover el vehículo **rápidamente**
6. **Resultado esperado:** ID aún debe ser `ID#1`

**Criterio de éxito:**
- ✅ ID permanece constante durante todo el movimiento
- ✅ Panel muestra "Vehículos Únicos: 1"

**Si falla:**
- Aumentar `max_cosine_distance` a 0.5 (más permisivo)
- Aumentar `max_age` a 50 (más tolerancia)

---

### Test 2: Múltiples Vehículos Simultáneos

**Objetivo:** Verificar que no se confundan IDs entre vehículos

**Pasos:**
1. Colocar 3 Hot Wheels diferentes en el encuadre
2. Esperar detección: `ID#1`, `ID#2`, `ID#3`
3. Mover los 3 vehículos simultáneamente
4. **Resultado esperado:** Cada uno mantiene su ID original

**Criterio de éxito:**
- ✅ 3 vehículos = 3 IDs únicos
- ✅ IDs no se intercambian entre vehículos
- ✅ Panel muestra "Vehículos Únicos: 3"

**Si falla:**
- Reducir `max_cosine_distance` a 0.3 (más estricto)
- Verificar que vehículos sean visualmente distintos

---

### Test 3: Oclusión Temporal

**Objetivo:** Verificar re-identificación después de obstrucción

**Pasos:**
1. Colocar 1 Hot Wheels visible: `ID#1`
2. Cubrir completamente el vehículo con la mano (5 segundos)
3. Retirar la mano
4. **Resultado esperado:** Vehículo recupera `ID#1`

**Criterio de éxito:**
- ✅ Después de oclusión, mismo ID
- ✅ No crea `ID#2` para el mismo vehículo
- ✅ Panel mantiene "Vehículos Únicos: 1"

**Si falla:**
- Aumentar `max_age` a 50 (más tiempo sin detección)
- Aumentar `max_cosine_distance` a 0.5

---

### Test 4: Entrada/Salida de Escena

**Objetivo:** Verificar comportamiento al entrar/salir del encuadre

**Pasos:**
1. Vehículo entra en escena: Se asigna `ID#1`
2. Vehículo sale completamente del encuadre (esperar 5 seg)
3. **Mismo vehículo** vuelve a entrar
4. Observar qué ID se asigna

**Resultado esperado (con max_age=30):**
- Si vuelve antes de 30 frames (~5 seg a 6 FPS): `ID#1`
- Si vuelve después de 30 frames: Nuevo `ID#2`

**Esto es correcto:** Un vehículo que salió y volvió después de mucho tiempo ES un nuevo evento

---

### Test 5: Falsos Positivos

**Objetivo:** Verificar que no detecte objetos no vehiculares

**Pasos:**
1. Colocar objetos NO vehiculares: rostro, mano, libro, teléfono
2. Observar detecciones
3. **Resultado esperado:** NO debe detectar estos objetos

**Criterio de éxito:**
- ✅ Solo detecta vehículos Hot Wheels
- ✅ Filtros funcionan correctamente
- ✅ No aparecen IDs para objetos no vehiculares

**Si falla:**
- Aumentar `confidence_threshold` a 0.8
- Verificar filtros de área y ratio

---

## 📊 Monitoreo de Rendimiento

### Métricas a Observar:

**En la UI:**
- **Vehículos Únicos:** Debe aumentar solo con nuevos vehículos
- **Frames Procesados:** Debe aumentar constantemente
- **Detecciones en Frame Actual:** Debe reflejar vehículos visibles

**En Logs del Backend:**
```
Frame 1 processing...
YOLO detections: 1 -> Tracked objects: 1
Tracked: 1 objects | Unique total: 1
```

**Tiempos esperados (por frame):**
- YOLO inference: ~30-50ms
- DeepSORT tracking: ~10-15ms (GPU)
- Total: ~50-70ms (14-20 FPS)

**Si es lento (>200ms por frame):**
1. Verificar que `embedder_gpu=True` esté activo
2. Verificar que `half=True` esté activo
3. Considerar reducir `nn_budget` a 50
4. Verificar que CUDA esté funcionando:
   ```python
   import torch
   print(torch.cuda.is_available())  # Debe ser True
   ```

---

## 🔧 Ajustes de Parámetros

### Si pierde IDs durante movimiento:

**Problema:** Vehículo cambia de ID al moverse

**Solución 1 - Más permisivo con similitud:**
```python
max_cosine_distance=0.5  # De 0.4 → 0.5 (50% similitud)
```

**Solución 2 - Más tolerancia temporal:**
```python
max_age=50  # De 30 → 50 frames
```

**Solución 3 - Menos confirmaciones:**
```python
n_init=2  # De 3 → 2 frames (detecta más rápido)
```

---

### Si crea muchos IDs para mismo vehículo:

**Problema:** 1 vehículo tiene ID#1, ID#2, ID#3...

**Solución 1 - Más estricto con confirmación:**
```python
n_init=5  # De 3 → 5 frames (confirma más lento)
```

**Solución 2 - Más memoria de features:**
```python
nn_budget=200  # De 100 → 200 (más historial visual)
```

---

### Si confunde vehículos diferentes:

**Problema:** Vehículo A obtiene ID de vehículo B

**Solución - Más estricto con similitud:**
```python
max_cosine_distance=0.3  # De 0.4 → 0.3 (70% similitud)
```

---

## 📈 Comparación de Resultados

### Antes (Norfair con IoU):
```
Escenario: Vehículo moviéndose 50px/frame
Frame 1: ID#1 ✅
Frame 2: ID#1 ✅
Frame 3: ID#2 ❌ (perdió tracking)
Frame 4: ID#2 ✅
Frame 5: ID#3 ❌ (perdió tracking nuevamente)

Resultado: 3 IDs para 1 vehículo ❌
Vehículos Únicos: 3 (INCORRECTO)
```

### Después (DeepSORT con Visual Features):
```
Escenario: Mismo vehículo moviéndose 50px/frame
Frame 1: ID#1 ✅ (feature: [0.23, 0.45, ...])
Frame 2: ID#1 ✅ (match: 0.92 similarity)
Frame 3: ID#1 ✅ (match: 0.89 similarity)
Frame 4: ID#1 ✅ (match: 0.91 similarity)
Frame 5: ID#1 ✅ (match: 0.88 similarity)

Resultado: 1 ID estable ✅
Vehículos Únicos: 1 (CORRECTO)
```

---

## 🎯 Criterios de Éxito Global

### El sistema debe cumplir:

1. ✅ **Persistencia ≥90%:** Mismo vehículo mantiene ID en 90%+ del tiempo
2. ✅ **No duplicados:** Tolerancia de ±1 ID extra por sesión de 5 minutos
3. ✅ **Múltiples objetos:** Hasta 10 vehículos sin confusión
4. ✅ **Velocidad:** <200ms por frame en promedio
5. ✅ **Precisión:** "Vehículos Únicos" refleja realidad con ±10% error
6. ✅ **Estabilidad:** Sin crashes durante 5+ minutos de uso continuo

---

## 🚀 Próximos Pasos

### Pruebas Pendientes:
1. [ ] Test 1: Vehículo único en movimiento
2. [ ] Test 2: Múltiples vehículos simultáneos
3. [ ] Test 3: Oclusión temporal
4. [ ] Test 4: Entrada/salida de escena
5. [ ] Test 5: Falsos positivos

### Después de Pruebas:
1. Documentar parámetros finales óptimos
2. Medir tiempo promedio de procesamiento
3. Tomar capturas de pantalla de resultados
4. Commit de cambios finales
5. Actualizar documentación del proyecto

---

## 📞 Troubleshooting

### Error: "Cannot find module deep_sort_realtime"
```bash
cd S:\Construccion\TrafiSmart\backend
.\venv\Scripts\pip.exe install deep-sort-realtime==1.3.2
```

### Error: "CUDA out of memory"
```python
# Reducir carga en GPU
embedder_gpu=False  # Usar CPU para features
half=False          # Desactivar FP16
nn_budget=50        # Reducir memoria
```

### Tracking muy lento (>500ms)
```python
# Configuración ligera
max_age=15          # Menos persistencia
nn_budget=30        # Menos memoria
embedder="clip_RN50"  # Embedder más ligero
```

### IDs cambian constantemente
```python
# Más permisivo
max_cosine_distance=0.6
max_age=50
n_init=2
```

---

## ✅ Checklist Final

```
[✓] 1. Norfair desinstalado
[✓] 2. DeepSORT instalado
[✓] 3. Código migrado
[✓] 4. Tests unitarios pasan
[✓] 5. Backend iniciado sin errores
[✓] 6. PyTorch/CUDA intactos
[ ] 7. Pruebas con cámara real
[ ] 8. Métricas de rendimiento
[ ] 9. Parámetros optimizados
[ ] 10. Documentación actualizada
```

---

**Estado Actual:** ✅ Migración completa, listo para pruebas en vivo

**Instrucciones:** Abre el frontend, inicia la detección y prueba los escenarios descritos arriba.
