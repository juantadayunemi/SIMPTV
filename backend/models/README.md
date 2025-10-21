# 🧠 Modelos de IA - SIMPTV# Modelos de Detección de Vehículos y Placas



Modelos pre-entrenados para análisis de tráfico vehicular en tiempo real.## 🎯 Arquitectura Implementada



---**MobileNetSSD + HaarCascade + PaddleOCR**



## 📦 **Arquitectura Implementada**Esta carpeta contiene los modelos pre-entrenados necesarios para el análisis de tráfico:



### **YOLOv4-Tiny + HaarCascade + PaddleOCR**### 1. **MobileNetSSD** (Detección de Vehículos)

- **Archivo**: `MobileNetSSD_deploy.caffemodel` (~23 MB)

```- **Configuración**: `MobileNetSSD_deploy.prototxt`

Video/Stream- **Función**: Detecta vehículos (automóviles, autobuses, bicicletas, motocicletas)

    ↓- **Velocidad**: 3-5x más rápido que YOLOv5

YOLOv4-Tiny (Detección de vehículos) ← 150-250 FPS- **Framework**: OpenCV DNN (Caffe)

    ↓

ROI Vehículo (Bounding box)### 2. **HaarCascade** (Detección de Placas)

    ↓- **Archivo**: `haarcascade_russian_plate_number.xml` (~1.5 MB)

HaarCascade (Detección de placa) ← 100+ FPS- **Función**: Detecta regiones de placas vehiculares en ROI de vehículos

    ↓- **Framework**: OpenCV (clasificador pre-entrenado)

ROI Placa (Región de interés)

    ↓### 3. **PaddleOCR** (Reconocimiento de Texto)

Preprocesamiento (Grayscale, Binary, Contrast)- **Modelos**: Se descargan automáticamente al inicializar PaddleOCR

    ↓- **Función**: Reconoce texto en placas detectadas

PaddleOCR (Lectura de texto) ← 50-70ms/placa- **Framework**: PaddlePaddle

    ↓

Resultado: Tipo vehículo + Texto placa---

```

## 📥 Instalación de Modelos

---

### Opción 1: Script Automático (Recomendado)

## 🎯 **Modelos Incluidos**

```bash

### 1. **YOLOv4-Tiny** - Detección de Vehículoscd S:\Construccion\SIMPTV\backend

python models\download_models.py

**Archivos:**```

- `yolov4-tiny.weights` (23.1 MB) - Pesos del modelo

- `yolov4-tiny.cfg` (3.2 KB) - Configuración de red### Opción 2: Descarga Manual

- `coco.names` (0.6 KB) - 80 clases COCO

Si el script automático falla, descarga manualmente:

**Características:**

- **Velocidad:** 150-250 FPS (CPU), 300+ FPS (GPU CUDA)1. **MobileNetSSD Prototxt**

- **Precisión:** 40-60% mAP (suficiente para tráfico)   ```

- **Clases de vehículos:**   https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.prototxt

  - 1: bicycle   ```

  - 2: car

  - 3: motorcycle2. **MobileNetSSD Model**

  - 5: bus   ```

  - 7: truck   https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.caffemodel

  - 6: train   ```

  - 8: boat

- **Framework:** OpenCV DNN (nativo, sin conversiones)3. **HaarCascade Placas**

- **GPU:** CUDA nativo en OpenCV DNN   ```

   https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_russian_plate_number.xml

**Descargar:**   ```

```bash

python models/download_yolov4_tiny.pyGuarda todos los archivos en esta carpeta: `S:\Construccion\SIMPTV\backend\models\`

```

---

---

## ✅ Verificación

### 2. **HaarCascade** - Detección de Placas

Después de descargar, verifica que tienes estos archivos:

**Archivo:**

- `haarcascade_russian_plate_number.xml` (73.7 KB)```

models/

**Características:**├── download_models.py                    (Script de descarga)

- **Función:** Detecta regiones de placas vehiculares├── verify_installation.py                (Script de verificación)

- **Velocidad:** 100+ FPS├── README.md                             (Este archivo)

- **Compatibilidad:** Global (no solo placas rusas)├── MobileNetSSD_deploy.prototxt          (29 KB)

- **Framework:** OpenCV nativo (cv2.CascadeClassifier)├── MobileNetSSD_deploy.caffemodel        (23 MB)

├── haarcascade_russian_plate_number.xml  (74 KB)

**Descargar:**└── __init__.py                           (Paquete Python)

```bash```

python models/download_haarcascade.py

```Para verificar que los modelos están correctamente instalados:



---```bash

python models\verify_installation.py

### 3. **PaddleOCR** - Reconocimiento de Texto```



**Modelos:**---

- Se descargan automáticamente al primer uso

- `~150 MB` en total## 🚀 Uso en el Código



**Características:**```python

- **Función:** Lee texto de placas vehicularesfrom pathlib import Path

- **Velocidad:** 50-70ms por placaimport cv2

- **Idiomas:** Multilingüe (incluye español, inglés, números)

- **Framework:** PaddlePaddleMODELS_DIR = Path(__file__).resolve().parent.parent / 'models'



**Instalación:**# Cargar MobileNetSSD con GPU CUDA (si está disponible)

```bashnet = cv2.dnn.readNetFromCaffe(

pip install paddleocr paddlepaddle    str(MODELS_DIR / 'MobileNetSSD_deploy.prototxt'),

# Los modelos se descargan automáticamente    str(MODELS_DIR / 'MobileNetSSD_deploy.caffemodel')

```)



---# Activar GPU CUDA para 3-5x más velocidad

try:

## 🚀 **Instalación Rápida**    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)

    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

### Opción 1: Script Automático (Recomendado)    print("✅ GPU CUDA activada")

except:

```bash    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)

# Descargar todos los modelos    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

cd backend    print("💻 Usando CPU optimizada")

python models/download_yolov4_tiny.py

python models/download_haarcascade.py# Cargar HaarCascade

plate_cascade = cv2.CascadeClassifier(

# Verificar instalación    str(MODELS_DIR / 'haarcascade_russian_plate_number.xml')

python models/verify_installation.py)

``````



### Opción 2: Descarga Manual---



Si los scripts fallan, descarga manualmente:## 📊 Rendimiento Esperado



1. **YOLOv4-Tiny Weights:**### CPU (Intel Core i5/i7 o AMD Ryzen 5/7)

   ```- **MobileNetSSD**: 60-90 FPS (1920x1080)

   https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.weights- **HaarCascade**: 100-150 FPS

   ```- **PaddleOCR**: 50-70ms por placa

- **Total end-to-end**: 50-70 FPS

2. **YOLOv4-Tiny Config:**

   ```### GPU CUDA (NVIDIA GTX 1060+ o RTX series)

   https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg- **MobileNetSSD**: 150-200 FPS (1920x1080)

   ```- **HaarCascade**: 150+ FPS

- **PaddleOCR**: 30-40ms por placa

3. **COCO Names:**- **Total end-to-end**: 100-120 FPS

   ```

   https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names---

   ```

## 🔧 Optimizaciones Aplicadas

4. **HaarCascade:**

   ```1. **Resolución reducida**: Frames procesados a 800px (60% más rápido)

   https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_russian_plate_number.xml2. **Frame skipping**: Videos 60 FPS procesados a 30 FPS efectivo

   ```3. **Calidad JPEG**: 45-50 para balance velocidad/calidad

4. **GPU CUDA**: Activación automática si disponible

Colocar todos los archivos en `backend/models/`5. **Procesamiento adaptativo**: Ajuste dinámico según FPS de origen



------



## 📊 **Comparativa con Alternativas**## ❓ Troubleshooting



| Modelo | Velocidad | Precisión | Tamaño | GPU | Complejidad |# PaddleOCR (descarga modelos automáticamente)

|--------|-----------|-----------|--------|-----|-------------|from paddleocr import PaddleOCR

| **YOLOv4-Tiny** | 150-250 FPS | 40-60% | 23 MB | ✅ Nativo | Simple |ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)

| YOLOv8n-ONNX | 80-100 FPS | 80-90% | 12 MB | ✅ Requiere conversión | Media |```

| MobileNetSSD | 60-90 FPS | 60% | 23 MB | ✅ | Simple |

| YOLOv5s | 50-80 FPS | 70-80% | 14 MB | ✅ PyTorch | Alta |---



**Veredicto:** YOLOv4-Tiny es **óptimo para análisis de tráfico en tiempo real** porque:## 📊 Comparación con YOLOv5

- ✅ 2-3x más rápido que alternativas

- ✅ Suficiente precisión para vehículos| Métrica | YOLOv5 (Anterior) | MobileNetSSD (Nuevo) |

- ✅ Simple (sin conversiones ni dependencias pesadas)|---------|-------------------|----------------------|

- ✅ GPU CUDA nativo| **Velocidad** | ~35-50 FPS | ~60-90 FPS |

| **Tamaño** | ~81 MB | ~23 MB |

---| **Memoria** | ~2-3 GB | ~500 MB |

| **Dependencias** | PyTorch/ONNX | Solo OpenCV |

## 🔧 **Uso en Código**| **Precisión** | 95% | 90-92% |



```python---

import cv2

## 🔧 Troubleshooting

# Cargar YOLOv4-Tiny

net = cv2.dnn.readNetFromDarknet(### Error: "Modelos no encontrados"

    'models/yolov4-tiny.cfg',```bash

    'models/yolov4-tiny.weights'python models\download_models.py

)```



# Activar GPU CUDA (opcional)### Error: "FileNotFoundError"

net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)Verifica que estás ejecutando desde la raíz del backend:

net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)```bash

cd S:\Construccion\SIMPTV\backend

# Cargar clasespython models\download_models.py

with open('models/coco.names', 'r') as f:```

    classes = f.read().strip().split('\n')

### Descargas lentas o fallan

# Cargar HaarCascadeDescarga manual y coloca archivos en `models/`

plate_cascade = cv2.CascadeClassifier(

    'models/haarcascade_russian_plate_number.xml'---

)

## 📝 Notas

# PaddleOCR (lazy loading)

from paddleocr import PaddleOCR- Los modelos de PaddleOCR se descargan automáticamente en `~/.paddleocr/`

ocr = PaddleOCR(use_angle_cls=True, lang='en')- MobileNetSSD puede detectar 20 clases, usamos solo: bicycle, bus, car, motorbike

```- HaarCascade funciona mejor con placas rectangulares estilo europeo/ruso

- Para placas de otros países, considera entrenar un modelo personalizado

---

---

## 🎯 **Rendimiento Esperado**

## 🔄 Actualización de Modelos

### Con CPU (Intel i5/i7/Ryzen 5/7):

```Para actualizar a versiones más nuevas:

✅ YOLOv4-Tiny: 150-250 FPS

✅ HaarCascade: 100+ FPS1. Elimina los archivos `.caffemodel` y `.xml`

✅ PaddleOCR: 50-70ms/placa2. Ejecuta nuevamente `download_models.py`

✅ Pipeline completo: 60-90 FPS3. O descarga manualmente desde las URLs oficiales

```

---

### Con GPU CUDA (NVIDIA GTX/RTX):

```## 📚 Referencias

🚀 YOLOv4-Tiny: 300-500 FPS

🚀 HaarCascade: 150+ FPS- [MobileNet-SSD GitHub](https://github.com/chuanqi305/MobileNet-SSD)

🚀 PaddleOCR: 30-40ms/placa- [OpenCV DNN Module](https://docs.opencv.org/master/d2/d58/tutorial_table_of_content_dnn.html)

🚀 Pipeline completo: 90-150 FPS- [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR)

```- [HaarCascades OpenCV](https://github.com/opencv/opencv/tree/master/data/haarcascades)


---

## 📝 **Notas**

- **YOLOv4-Tiny** está optimizado para velocidad, no precisión máxima
- **40-60% mAP** es suficiente para detección de vehículos en tráfico
- **HaarCascade** funciona mejor con placas horizontales
- **PaddleOCR** requiere preprocesamiento (grayscale, binary, contrast)
- **GPU CUDA** requiere OpenCV compilado con soporte CUDA

---

## 🐛 **Troubleshooting**

### Error: "Cannot find yolov4-tiny.weights"
```bash
python models/download_yolov4_tiny.py
```

### Error: "GPU not available"
```python
# Usar CPU (automático si GPU no disponible)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
```

### Error: "PaddleOCR no detecta texto"
```python
# Mejorar preprocesamiento
gray = cv2.cvtColor(plate_roi, cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
result = ocr.ocr(thresh, cls=True)
```

---

## 📚 **Referencias**

- [YOLOv4-Tiny Paper](https://arxiv.org/abs/2004.10934)
- [Darknet Repository](https://github.com/AlexeyAB/darknet)
- [OpenCV DNN Module](https://docs.opencv.org/master/d2/d58/tutorial_table_of_content_dnn.html)
- [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR)
