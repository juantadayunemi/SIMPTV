import cv2
import time
import torch
import threading
import queue
from ultralytics import YOLO
import os

# ========================
# CONFIGURACIÓN
# ========================
video_path = os.getenv("VIDEO_PATH") or r"D:\TrafiSmart\backend\videos\trafico.mp4"
model_path = os.getenv("YOLO_MODEL")

if not model_path or not os.path.exists(model_path):
    raise FileNotFoundError(f"No se encontró el modelo en la ruta: {model_path}")

if not os.path.exists(video_path):
    raise FileNotFoundError(f"No se encontró el video en la ruta: {video_path}")

# ========================
# PARÁMETROS OPTIMIZADOS
# ========================
# CAMBIA ESTOS VALORES PARA AJUSTAR VELOCIDAD:

# --- CONFIGURACIÓN ACTUAL (42 FPS) ---
# BATCH_SIZE = 16
# FRAME_SKIP = 1
# CONF_THRESHOLD = 0.4
# MAX_DETECTIONS = 50
# IMG_SIZE = 640

# --- CONFIGURACIÓN MODERADA (~60-70 FPS) ---
BATCH_SIZE = 20
FRAME_SKIP = 1
CONF_THRESHOLD = 0.5
MAX_DETECTIONS = 40
IMG_SIZE = 640

# --- CONFIGURACIÓN RÁPIDA (~80-100 FPS) ---
# BATCH_SIZE = 24
# FRAME_SKIP = 2          # Analiza 1 de cada 2 frames
# CONF_THRESHOLD = 0.5
# MAX_DETECTIONS = 30
# IMG_SIZE = 416

# --- CONFIGURACIÓN ULTRA RÁPIDA (~120-150 FPS) ---
# BATCH_SIZE = 32
# FRAME_SKIP = 3          # Analiza 1 de cada 3 frames
# CONF_THRESHOLD = 0.6
# MAX_DETECTIONS = 20
# IMG_SIZE = 320

QUEUE_SIZE = 48         # Buffer grande
USE_FP16 = True
IOU_THRESHOLD = 0.5

# ========================
# GPU Y MODELO
# ========================
if torch.cuda.is_available():
    device = 'cuda'
    gpu_name = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"✅ GPU: {gpu_name} ({vram:.1f} GB VRAM)")
else:
    device = 'cpu'
    print("⚠️ No GPU detectada, usando CPU")

print(f"📦 Cargando modelo...")
model = YOLO(model_path)
model.to(device)

if USE_FP16 and device == 'cuda':
    model.model.half()
    print(f"⚡ FP16 activado")

print(f"✅ Modelo cargado\n")

# ========================
# COLAS
# ========================
frame_queue = queue.Queue(maxsize=QUEUE_SIZE)
result_queue = queue.Queue(maxsize=QUEUE_SIZE)

stop_flag = threading.Event()
read_complete = threading.Event()

# ========================
# LECTURA SECUENCIAL OPTIMIZADA
# ========================
def read_frames_sequential(cap, reader_id, total_readers):
    """Lee frames de manera secuencial intercalada"""
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Cada lector empieza en una posición diferente
    start_pos = reader_id * (total_frames // total_readers)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_pos)
    
    batch = []
    batch_ids = []
    
    while not stop_flag.is_set():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Saltar frames si está configurado
        if FRAME_SKIP > 1:
            for _ in range(FRAME_SKIP - 1):
                if not cap.read()[0]:
                    break
        
        # Resize
        frame = cv2.resize(frame, (640, 360), interpolation=cv2.INTER_LINEAR)
        
        current_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        batch.append(frame)
        batch_ids.append(current_pos)
        frame_count += 1
        
        # Enviar batch completo
        if len(batch) >= BATCH_SIZE:
            frame_queue.put((batch_ids.copy(), batch.copy()))
            batch.clear()
            batch_ids.clear()
        
        # Saltar al siguiente segmento de este lector
        next_pos = current_pos + (total_readers - 1) * FRAME_SKIP
        if next_pos >= start_pos + (total_frames // total_readers):
            break
        cap.set(cv2.CAP_PROP_POS_FRAMES, next_pos)
    
    # Enviar último batch
    if batch:
        frame_queue.put((batch_ids, batch))
    
    print(f"📹 Lector {reader_id} completado: {frame_count} frames")

# ========================
# LECTURA SIMPLE (MEJOR OPCIÓN)
# ========================
def read_frames_simple(cap):
    """Lectura simple y rápida - UN SOLO THREAD"""
    frame_count = 0
    batch = []
    batch_ids = []
    
    while not stop_flag.is_set():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Saltar frames si está configurado
        if FRAME_SKIP > 1:
            for _ in range(FRAME_SKIP - 1):
                cap.read()
        
        # Resize rápido
        frame = cv2.resize(frame, (640, 360), interpolation=cv2.INTER_LINEAR)
        
        batch.append(frame)
        batch_ids.append(frame_count)
        frame_count += 1
        
        # Enviar batch completo
        if len(batch) >= BATCH_SIZE:
            frame_queue.put((batch_ids.copy(), batch.copy()))
            batch.clear()
            batch_ids.clear()
    
    # Enviar último batch
    if batch:
        frame_queue.put((batch_ids, batch))
    
    frame_queue.put(None)  # Señal de fin
    read_complete.set()
    print(f"📹 Lectura completada: {frame_count} frames")

# ========================
# PROCESADOR GPU OPTIMIZADO
# ========================
def process_batches():
    """Procesa batches con configuración optimizada"""
    total_processed = 0
    
    while not stop_flag.is_set():
        try:
            batch_data = frame_queue.get(timeout=1)
            
            if batch_data is None:
                break
            
            batch_ids, frames = batch_data
            
            # Inferencia optimizada
            if USE_FP16 and device == 'cuda':
                with torch.amp.autocast('cuda'):
                    results = model.predict(
                        frames,
                        device=device,
                        verbose=False,
                        half=True,
                        imgsz=IMG_SIZE,
                        conf=CONF_THRESHOLD,    # ← Más alto = más rápido
                        iou=IOU_THRESHOLD,
                        max_det=MAX_DETECTIONS,  # ← Limitar detecciones
                        agnostic_nms=True        # ← NMS más rápido
                    )
            else:
                results = model.predict(
                    frames,
                    device=device,
                    verbose=False,
                    imgsz=IMG_SIZE,
                    conf=CONF_THRESHOLD,
                    iou=IOU_THRESHOLD,
                    max_det=MAX_DETECTIONS
                )
            
            # Enviar resultados
            for frame_id, result in zip(batch_ids, results):
                result_queue.put((frame_id, result))
            
            total_processed += len(frames)
            
        except queue.Empty:
            if read_complete.is_set() and frame_queue.empty():
                break
            continue
        except Exception as e:
            print(f"❌ Error GPU: {e}")
    
    print(f"✅ GPU completada: {total_processed} frames")

# ========================
# MAIN
# ========================
def main():
    print(f"{'='*60}")
    print(f"🎬 PROCESAMIENTO OPTIMIZADO YOLO")
    print(f"{'='*60}")
    print(f"📊 Configuración:")
    print(f"   - Batch size: {BATCH_SIZE}")
    print(f"   - Queue size: {QUEUE_SIZE}")
    print(f"   - Frame skip: {FRAME_SKIP}")
    print(f"   - Image size: {IMG_SIZE}")
    print(f"   - Confidence: {CONF_THRESHOLD}")
    print(f"   - Max detections: {MAX_DETECTIONS}")
    print(f"   - FP16: {USE_FP16}")
    print(f"{'='*60}\n")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"No se pudo abrir el video")
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"📹 Video: {total_frames} frames @ {video_fps:.2f} FPS\n")
    
    start_time = time.time()
    
    # Usar lectura SIMPLE (más eficiente)
    read_thread = threading.Thread(target=read_frames_simple, args=(cap,), daemon=True)
    read_thread.start()
    
    # Iniciar GPU
    gpu_thread = threading.Thread(target=process_batches, daemon=True)
    gpu_thread.start()
    
    # Monitor de progreso
    frame_count = 0
    last_print = start_time
    last_count = 0
    
    while True:
        try:
            frame_id, result = result_queue.get(timeout=2)
            frame_count += 1
            
            current_time = time.time()
            if current_time - last_print >= 2:
                elapsed = current_time - start_time
                instant_fps = (frame_count - last_count) / (current_time - last_print)
                avg_fps = frame_count / elapsed
                progress = (frame_count / total_frames) * 100
                
                print(f"⚡ {frame_count}/{total_frames} ({progress:.1f}%) | "
                      f"Avg: {avg_fps:.1f} FPS | Instant: {instant_fps:.1f} FPS")
                
                last_print = current_time
                last_count = frame_count
                
        except queue.Empty:
            if not gpu_thread.is_alive():
                break
    
    # Esperar threads
    read_thread.join()
    gpu_thread.join()
    cap.release()
    
    # Resultados
    elapsed = time.time() - start_time
    fps = frame_count / elapsed
    speedup = fps / video_fps
    
    print(f"\n{'='*60}")
    print(f"🏁 RESULTADOS FINALES")
    print(f"{'='*60}")
    print(f"🎞️  Frames procesados: {frame_count}")
    print(f"⏱️  Tiempo total: {elapsed:.2f} s")
    print(f"⚡ FPS promedio: {fps:.2f}")
    print(f"📹 FPS del video: {video_fps:.2f}")
    print(f"🚀 Velocidad: {speedup:.2f}x tiempo real")
    
    if device == 'cuda':
        vram_used = torch.cuda.memory_allocated() / 1024**3
        vram_max = torch.cuda.max_memory_allocated() / 1024**3
        print(f"💾 VRAM: {vram_used:.2f} GB (max: {vram_max:.2f} GB)")
    
    print(f"{'='*60}\n")
    
    # Sugerencias
    if fps < video_fps:
        print("💡 SUGERENCIAS PARA MEJORAR:")
        print(f"   - Aumentar CONF_THRESHOLD a 0.5 o 0.6")
        print(f"   - Reducir MAX_DETECTIONS a 30")
        print(f"   - Cambiar FRAME_SKIP a 2 (analiza 1 de cada 2)")
        print(f"   - Reducir IMG_SIZE a 416\n")
    
    if device == 'cuda':
        torch.cuda.empty_cache()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Interrumpido")
        stop_flag.set()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()