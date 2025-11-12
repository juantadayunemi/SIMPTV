# 🎯 Configuración de Detección YOLO - TrafiSmart

## ⚙️ Parámetros Actuales (Optimizados)

### Umbral de Confianza
```python
confidence_threshold = 0.5  # Bajado de 0.7 a 0.5
```
**¿Qué hace?** 
- Acepta detecciones con 50% de confianza o más
- Más bajo = más detecciones (incluso menos seguras)
- Más alto = menos detecciones (solo las muy seguras)

**Recomendaciones:**
- Juguetes/objetos pequeños: `0.4 - 0.5`
- Vehículos reales lejanos: `0.5 - 0.6`
- Vehículos reales cercanos: `0.6 - 0.8`

---

### Filtros de Validación

#### 1️⃣ Área Mínima
```python
area_minima = 1000  # píxeles (bajado de 5000)
```
**¿Qué hace?**
- Descarta detecciones muy pequeñas
- Protege contra ruido y artefactos

**Ajustar si:**
- Objetos muy pequeños no se detectan → **Bajar a 500**
- Muchos falsos positivos pequeños → **Subir a 2000**

#### 2️⃣ Ratio Ancho/Alto
```python
ratio_min = 0.8  # (bajado de 1.1)
ratio_max = 4.5  # (subido de 3.5)
```
**¿Qué hace?**
- Define la forma típica de un vehículo
- `ratio < 1.0` = Más alto que ancho (motos, personas)
- `ratio > 3.0` = Mucho más ancho que alto (camiones)

**Formas típicas:**
- **Motocicleta:** 0.8 - 1.2
- **Auto:** 1.5 - 2.5
- **Camión:** 2.0 - 4.0
- **Rostro:** 0.9 - 1.1 (cuadrado)

**Ajustar si:**
- Motos no se detectan → **Bajar min a 0.6**
- Camiones no se detectan → **Subir max a 5.0**

#### 3️⃣ Zona Vertical
```python
zona_minima = 0.20  # 20% superior del frame (bajado de 0.35)
```
**¿Qué hace?**
- Descarta objetos en el cielo/zona muy alta
- Evita detectar logos, textos, etc.

**Ajustar si:**
- Objetos arriba no se detectan → **Bajar a 0.10**
- Muchos falsos positivos arriba → **Subir a 0.30**

#### 4️⃣ Filtro Anti-Rostros (NUEVO)
```python
if 0.9 < ratio < 1.3 and area < 8000:
    # Es probablemente un rostro
    return False
```
**¿Qué hace?**
- Detecta formas cuadradas pequeñas (típicas de rostros)
- Evita falsos positivos con personas

**Ajustar si:**
- Autos pequeños/cuadrados se filtran → **Subir area a 10000**
- Rostros aún se detectan → **Expandir rango: 0.8 < ratio < 1.4**

---

## 🔧 Cómo Ajustar los Parámetros

### Opción 1: Temporal (para pruebas)
Edita directamente en:
```
backend/apps/streaming/services/yolo_processor.py
```

### Opción 2: Permanente
Crea variables de entorno en `.env`:
```bash
YOLO_CONFIDENCE=0.5
YOLO_MIN_AREA=1000
YOLO_MIN_RATIO=0.8
YOLO_MAX_RATIO=4.5
YOLO_MIN_ZONE=0.20
```

---

## 📊 Tabla de Valores Recomendados

| Escenario | Confidence | Min Area | Ratio Min-Max | Zona Min |
|-----------|-----------|----------|---------------|----------|
| **Juguetes Hot Wheels** | 0.4-0.5 | 500-1000 | 0.8-5.0 | 0.10 |
| **Vehículos reales cerca** | 0.6-0.7 | 5000 | 1.0-4.0 | 0.25 |
| **Vehículos reales lejos** | 0.5-0.6 | 2000 | 1.0-4.5 | 0.15 |
| **Tráfico mixto** | 0.5 | 1500 | 0.8-4.5 | 0.20 |
| **Anti rostros estricto** | 0.6 | 3000 | 1.1-3.5 | 0.30 |

---

## 🧪 Testing Rápido

### 1. Probar con juguete
```python
# Valores súper permisivos
confidence = 0.3
min_area = 300
ratio_range = (0.5, 6.0)
```

### 2. Ver logs
Los logs te dirán por qué se rechazan:
```
⚠️ Rechazado por área pequeña: 800 < 1000
⚠️ Rechazado por ratio: 0.7 fuera de 0.8-4.5
⚠️ Rechazado por zona alta: y2=50 < 100
⚠️ Posible rostro detectado: ratio=1.0, area=5000
```

### 3. Ajustar iterativamente
1. Ver qué filtro rechaza tu objeto
2. Relajar ese filtro específico
3. Probar de nuevo

---

## 💡 Consejos

### Para detectar juguetes mejor:

1. **Iluminación:**
   - Más luz = mejor detección
   - Evita sombras fuertes

2. **Distancia:**
   - 30-60cm de la cámara es óptimo
   - Muy cerca o muy lejos dificulta

3. **Fondo:**
   - Fondo contrastante
   - Evita fondos con patrones complejos

4. **Ángulo:**
   - Vista lateral o 3/4 es mejor
   - Vista cenital es más difícil

### Si sigues teniendo problemas:

1. **Captura un screenshot** del juguete que no detecta
2. **Mira los logs** para ver por qué se rechaza
3. **Ajusta ese filtro específico**

---

## 📝 Archivos Modificados

- `backend/apps/streaming/services/yolo_processor.py` - Filtros mejorados
- Confianza bajada de 0.7 a 0.5
- Área mínima bajada de 5000 a 1000
- Ratio ampliado de 1.1-3.5 a 0.8-4.5
- Zona permitida ampliada de 0.35 a 0.20

---

**Fecha:** 10 de Noviembre, 2025
**Estado:** Optimizado para juguetes y objetos pequeños ✅
