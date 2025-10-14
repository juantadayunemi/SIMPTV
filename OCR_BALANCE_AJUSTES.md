# ⚖️ Ajustes de Balance OCR - Detección vs Precisión

## 🔴 Problema Reportado

**Situación**: Después de implementar restricciones muy estrictas en el OCR, el sistema NO detectó ninguna placa durante todo el análisis.

**Causa**: Parámetros demasiado restrictivos que bloqueaban incluso detecciones válidas.

---

## ✅ Ajustes Implementados (Balance)

### 1️⃣ **Parámetros OCR Balanceados**

#### ❌ ANTES (Demasiado restrictivo):
```python
min_size=20
text_threshold=0.75    # ❌ MUY ALTO
low_text=0.5           # ❌ MUY ALTO
width_ths=0.9          # ❌ MUY ALTO
height_ths=0.9         # ❌ MUY ALTO
confidence >= 0.4      # ❌ MUY ALTO
len(cleaned) >= 5      # ❌ Muy restrictivo
```

**Resultado**: ❌ **0 placas detectadas**

---

#### ✅ AHORA (Balanceado):
```python
min_size=15            # ⚖️ REDUCIDO: permite letras más pequeñas
text_threshold=0.6     # ⚖️ BALANCEADO: detecta mejor
low_text=0.4           # ⚖️ BALANCEADO: más sensible
width_ths=0.7          # ⚖️ BALANCEADO: menos estricto
height_ths=0.7         # ⚖️ BALANCEADO: menos estricto
confidence >= 0.25     # ⚖️ REDUCIDO: más permisivo inicial
len(cleaned) >= 4      # ⚖️ Acepta desde 4 caracteres
```

**Estrategia**: Detectar más candidatos inicialmente, pero validar estrictamente después.

---

### 2️⃣ **Validación de Formato (Sin cambios)**

Se mantiene la validación estricta:
```python
# ✅ DEBE tener letras Y números
has_letters = any(c.isalpha() for c in cleaned)
has_numbers = any(c.isdigit() for c in cleaned)

if has_letters and has_numbers:
    # ✅ Solo entonces se acepta
```

**Ejemplos válidos**:
- ✅ `ABC123` (6 chars, letras+números)
- ✅ `AB12` (4 chars mínimo)
- ✅ `XYZ789AB` (8 chars máximo)

**Ejemplos rechazados**:
- ❌ `TOYOTA` (solo letras)
- ❌ `123456` (solo números)
- ❌ `AB1` (muy corto < 4)

---

### 3️⃣ **Debugging Temporal**

Se agregaron logs para diagnosticar el problema:

```python
# Al buscar región de placa
if plate_roi is None:
    print(f"🔍 [DEBUG] Usando tercio inferior del vehículo para OCR")
else:
    print(f"🔍 [DEBUG] Región de placa detectada: {plate_roi.shape}")

# Durante OCR
print(f"🔍 [DEBUG] OCR encontró {len(results)} textos")
for text, confidence in results:
    print(f"🔍 [DEBUG] OCR raw: '{text}' (conf: {confidence:.2f})")

# Después de limpieza
print(f"🔍 [DEBUG] Cleaned: '{cleaned}' (len:{len(cleaned)}, letters:{has_letters}, numbers:{has_numbers})")

# Si pasa validación
print(f"✅ [DEBUG] Candidato aceptado: '{cleaned}' (conf: {confidence:.2f})")
```

**Propósito**: Ver exactamente qué está detectando el OCR y dónde se está filtrando.

---

## 📊 Comparación de Configuraciones

| Parámetro | Muy Restrictivo ❌ | Balanceado ✅ | Cambio |
|-----------|-------------------|---------------|--------|
| `min_size` | 20 | 15 | -25% |
| `text_threshold` | 0.75 | 0.6 | -20% |
| `low_text` | 0.5 | 0.4 | -20% |
| `width_ths` | 0.9 | 0.7 | -22% |
| `height_ths` | 0.9 | 0.7 | -22% |
| `confidence` | ≥0.4 | ≥0.25 | -37.5% |
| `longitud mín` | 5 | 4 | -1 char |
| **Validación** | ✅ Letras+Números | ✅ Letras+Números | Sin cambio |

---

## 🎯 Filosofía del Balance

### Estrategia de dos fases:

#### Fase 1: Detección (PERMISIVA)
- Umbrales de confianza bajos (0.25)
- Parámetros de OCR menos restrictivos
- **Objetivo**: Capturar todos los candidatos posibles

#### Fase 2: Validación (ESTRICTA)
- Requiere letras Y números
- Longitud válida (4-9 caracteres)
- Formato de placa correcto
- **Objetivo**: Filtrar falsos positivos

---

## 🔍 Casos de Uso

### Caso 1: Placa Clara y Bien Iluminada
```
Detección OCR: "ABC123" (conf: 0.85)
├─ ✅ Confianza ≥ 0.25
├─ ✅ Longitud: 6 (4-9)
├─ ✅ Tiene letras: ABC
├─ ✅ Tiene números: 123
└─ ✅ ACEPTADO
```

### Caso 2: Placa con Baja Confianza pero Válida
```
Detección OCR: "XY789" (conf: 0.28)
├─ ✅ Confianza ≥ 0.25
├─ ✅ Longitud: 5 (4-9)
├─ ✅ Tiene letras: XY
├─ ✅ Tiene números: 789
└─ ✅ ACEPTADO (con confianza reportada)
```

### Caso 3: Texto del Vehículo (Falso Positivo)
```
Detección OCR: "TOYOTA" (conf: 0.65)
├─ ✅ Confianza ≥ 0.25
├─ ✅ Longitud: 6 (4-9)
├─ ❌ Tiene letras: SÍ
├─ ❌ Tiene números: NO
└─ ❌ RECHAZADO
```

### Caso 4: Número de Serie (Falso Positivo)
```
Detección OCR: "123456" (conf: 0.45)
├─ ✅ Confianza ≥ 0.25
├─ ✅ Longitud: 6 (4-9)
├─ ❌ Tiene letras: NO
├─ ✅ Tiene números: SÍ
└─ ❌ RECHAZADO
```

---

## 🧪 Proceso de Prueba

### 1. **Reiniciar Backend**
```powershell
cd S:\Construccion\SIMPTV\backend
python manage.py runserver 8001
```

### 2. **Iniciar Análisis**
- Ir al frontend
- Iniciar análisis de video

### 3. **Observar Terminal con Logs de Debug**

Deberías ver:
```
🔍 [DEBUG] Usando tercio inferior del vehículo para OCR
🔍 [DEBUG] OCR encontró 3 textos
🔍 [DEBUG] OCR raw: 'ABC' (conf: 0.15)
🔍 [DEBUG] OCR raw: 'TOYOTA' (conf: 0.65)
🔍 [DEBUG] OCR raw: 'ABC123' (conf: 0.35)
🔍 [DEBUG] Cleaned: 'TOYOTA' (len:6, letters:True, numbers:False)
🔍 [DEBUG] Cleaned: 'ABC123' (len:6, letters:True, numbers:True)
✅ [DEBUG] Candidato aceptado: 'ABC123' (conf: 0.35)
🚗 ID:1 | Placa: ABC123 | Confianza: 35%
```

### 4. **Análisis de Logs**

#### Si NO detecta nada:
```
🔍 [DEBUG] OCR encontró 0 textos
```
**Problema**: La región de la placa o preprocessing no es adecuada.
**Acción**: Revisar preprocesamiento o región de detección.

#### Si detecta pero rechaza todo:
```
🔍 [DEBUG] OCR encontró 5 textos
🔍 [DEBUG] Cleaned: 'XYZ' (len:3, letters:True, numbers:False)
```
**Problema**: Textos muy cortos o sin números.
**Acción**: Verificar que las placas tengan formato correcto.

#### Si detecta y acepta:
```
✅ [DEBUG] Candidato aceptado: 'ABC123' (conf: 0.35)
🚗 ID:1 | Placa: ABC123 | Confianza: 35%
```
**✅ FUNCIONANDO CORRECTAMENTE**

---

## 🔧 Ajustes Opcionales Según Resultados

### A. Si NO detecta placas reales:

#### Opción 1: Reducir más el umbral de confianza
```python
# Línea ~604
if confidence >= 0.20:  # De 0.25 a 0.20
```

#### Opción 2: Reducir más los parámetros OCR
```python
# Línea ~581-594
min_size=10,           # De 15 a 10
text_threshold=0.5,    # De 0.6 a 0.5
width_ths=0.6,         # De 0.7 a 0.6
height_ths=0.6,        # De 0.7 a 0.6
```

#### Opción 3: Permitir placas más cortas
```python
# Línea ~608
if 3 <= len(cleaned) <= 9:  # De 4-9 a 3-9
```

---

### B. Si aún detecta muchos falsos positivos:

#### Opción 1: Aumentar umbral de confianza
```python
# Línea ~604
if confidence >= 0.35:  # De 0.25 a 0.35
```

#### Opción 2: Validación más estricta de formato
```python
# Línea ~608
if 5 <= len(cleaned) <= 7:  # Más restrictivo

# Además, agregar:
if has_letters and has_numbers:
    # Verificar que NO sea todo letras al inicio
    if not cleaned[:3].isalpha() or not cleaned[-2:].isdigit():
        continue
```

#### Opción 3: Requerir mejor proporción letras/números
```python
letter_count = sum(1 for c in cleaned if c.isalpha())
number_count = sum(1 for c in cleaned if c.isdigit())

# Proporción típica de placas: 3 letras + 3-4 números
if 2 <= letter_count <= 4 and 2 <= number_count <= 5:
    # Aceptar
```

---

## 📋 Checklist de Diagnóstico

Después de probar, verifica:

- [ ] **OCR está corriendo** (logs aparecen)
- [ ] **Detecta textos** (OCR encontró N textos > 0)
- [ ] **Limpia correctamente** (cleaned sin espacios/símbolos)
- [ ] **Valida formato** (muestra has_letters y has_numbers)
- [ ] **Acepta candidatos** (aparece "Candidato aceptado")
- [ ] **Muestra placa final** (🚗 ID:X | Placa: XXX)

---

## 🎯 Objetivo del Balance

| Métrica | Muy Restrictivo ❌ | Balanceado ✅ |
|---------|-------------------|---------------|
| **Detecciones** | 0 placas | 5-10 placas |
| **Precisión** | N/A | ~70-80% |
| **Falsos Positivos** | 0% | ~10-20% |
| **Recall** | 0% | ~60-70% |

**Estrategia**: Es mejor detectar algunas placas con ~70% precisión que no detectar nada.

---

## 📝 Próximos Pasos

1. ✅ **Probar con debugging activo**
2. 📊 **Analizar logs de OCR**
3. ⚖️ **Ajustar según resultados**
4. 🧹 **Remover logs de debug cuando funcione**
5. 📈 **Documentar configuración óptima**

---

**Fecha**: 2024-10-13  
**Status**: ⚖️ Balanceado - Listo para pruebas con debugging  
**Estrategia**: Detectar permisivo + Validar estricto  
**Autor**: GitHub Copilot
