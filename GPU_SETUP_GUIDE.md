# 🚀 Guía para Habilitar GPU (NVIDIA RTX 4050) en tu Proyecto

## 📊 Estado Actual

### ✅ Detectado:
- **GPU**: NVIDIA GeForce RTX 4050 Laptop
- **VRAM**: 6 GB
- **Driver**: 581.15
- **CUDA Version**: 13.0

### ❌ Problema:
- PyTorch instalado **SIN soporte CUDA**
- Todo corre en **CPU** → Lento, lag, freeze

### 📈 Mejora Esperada con GPU:
| Componente | CPU (Actual) | GPU (Después) | Mejora |
|------------|--------------|---------------|--------|
| **YOLO** | ~100ms/frame | ~10-15ms/frame | **6-10x más rápido** |
| **OCR** | ~200-300ms | ~50-80ms | **3-4x más rápido** |
| **FPS** | 2-5 FPS | **25-30 FPS** | **5-10x más fluido** |

---

## 🔧 Solución: Instalar PyTorch con CUDA

### Opción 1: **Instalación Automática (RECOMENDADO)**

```powershell
# 1. Activar entorno virtual
cd S:\Construccion\SIMPTV\backend
.\venv\Scripts\Activate.ps1

# 2. Desinstalar PyTorch actual (sin CUDA)
pip uninstall torch torchvision torchaudio -y

# 3. Instalar PyTorch con CUDA 12.1 (compatible con CUDA 13.0)
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 4. Verificar instalación
python check_gpu.py
```

### Opción 2: **CUDA 11.8 (Más estable)**

Si la opción 1 da problemas:

```powershell
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## ✅ Verificación

Después de instalar, ejecuta:

```powershell
python check_gpu.py
```

**Deberías ver**:
```
✅ CUDA disponible: True
📌 Versión CUDA: 12.1
🎮 GPU detectada: NVIDIA GeForce RTX 4050 Laptop GPU
💾 Memoria GPU total: 6.00 GB
✅ EasyOCR configurado con GPU: True
```

---

## 🎯 Optimizaciones Automáticas con GPU

Tu código **ya está preparado** para usar GPU automáticamente:

```python
# En video_processor.py línea 73-77
if device == "auto":
    self.device = "cuda" if torch.cuda.is_available() else "cpu"
```

Una vez instalado PyTorch con CUDA:
- ✅ YOLO correrá en GPU automáticamente
- ✅ EasyOCR usará GPU automáticamente
- ✅ Preprocessing con OpenCV seguirá en CPU (normal)

---

## 🚀 Optimizaciones Adicionales para GPU

### 1. **Habilitar FP16 (Half Precision)**

Modifica `video_processor.py` línea 192-203:

```python
results = self.model.track(
    frame,
    persist=True,
    tracker="bytetrack.yaml",
    conf=self.confidence_threshold,
    iou=self.iou_threshold,
    classes=[1, 2, 3, 5, 7],
    verbose=False,
    half=True,        # ✅ NUEVO: Usar FP16 en GPU (2x más rápido)
    imgsz=640,        # ✅ NUEVO: Reducir resolución (más rápido)
)
```

### 2. **Batch Processing para OCR**

Modifica `_detect_plate()` línea ~581:

```python
results = self.plate_reader.readtext(
    binary,
    allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
    paragraph=False,
    batch_size=4,     # ✅ CAMBIAR de 1 a 4 (procesar en lotes)
    # ... resto de parámetros
)
```

---

## 📊 Monitoreo de GPU

### Durante el análisis:

```powershell
# En otra terminal, ejecutar:
nvidia-smi -l 1
```

Verás:
- **GPU-Util**: Uso de GPU (debería estar 80-100% durante análisis)
- **Memory-Usage**: Memoria usada (de 6141 MiB total)
- **Power**: Consumo energético

---

## 🐛 Troubleshooting

### Problema: "CUDA out of memory"

**Solución 1**: Reducir batch size
```python
batch_size=1  # En lugar de 4
```

**Solución 2**: Reducir resolución YOLO
```python
imgsz=416  # En lugar de 640
```

**Solución 3**: Limpiar caché GPU
```python
import torch
torch.cuda.empty_cache()  # Al inicio de process_video()
```

### Problema: "RuntimeError: CUDA error"

**Solución**: Actualizar drivers NVIDIA
- Descargar desde: https://www.nvidia.com/download/index.aspx
- Buscar: GeForce RTX 4050 Laptop GPU

---

## 📋 Checklist de Instalación

- [ ] Desinstalar PyTorch sin CUDA
- [ ] Instalar PyTorch con CUDA 12.1
- [ ] Ejecutar `python check_gpu.py` → Ver "CUDA disponible: True"
- [ ] Reiniciar backend: `python manage.py runserver 8001`
- [ ] Iniciar análisis de video
- [ ] Verificar logs: "🚀 VideoProcessor usando device: cuda"
- [ ] Monitorear GPU: `nvidia-smi -l 1`
- [ ] Confirmar FPS mejorado (25-30 FPS)

---

## 🎯 Resultados Esperados

### Antes (CPU):
```
🚗 ID:1 | Placa: ABC123 | Confianza: 45%
[Tiempo: ~300ms por frame]
[FPS: 2-5]
```

### Después (GPU):
```
🚀 VideoProcessor usando device: cuda
✅ Modelo YOLO cargado en cuda
🚗 ID:1 | Placa: ABC123 | Confianza: 45%
[Tiempo: ~30-40ms por frame]
[FPS: 25-30] ⚡
```

---

## 💡 Notas Importantes

1. **Primera ejecución con GPU**: Puede ser lenta (compilando kernels CUDA)
2. **Después**: Velocidad constante y óptima
3. **Laptop**: Asegúrate de estar conectado a corriente (modo alto rendimiento)
4. **Temperatura**: La GPU puede llegar a 70-80°C (normal bajo carga)

---

**Fecha**: 2024-10-13  
**GPU**: NVIDIA GeForce RTX 4050 Laptop (6GB)  
**Status**: ⚠️ PyTorch sin CUDA → Necesita reinstalación  
**Mejora esperada**: **5-10x más rápido** con GPU habilitada
