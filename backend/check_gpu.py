"""Script para verificar disponibilidad y estado de GPU"""
import torch
import sys

print("=" * 60)
print("🔍 DIAGNÓSTICO DE GPU Y CUDA")
print("=" * 60)

# Verificar CUDA
cuda_available = torch.cuda.is_available()
print(f"\n✅ CUDA disponible: {cuda_available}")

if cuda_available:
    print(f"📌 Versión CUDA: {torch.version.cuda}")
    print(f"🎮 GPU detectada: {torch.cuda.get_device_name(0)}")
    print(f"💾 Memoria GPU total: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    print(f"💾 Memoria GPU libre: {torch.cuda.mem_get_info()[0] / 1024**3:.2f} GB")
    print(f"🔧 Capability: {torch.cuda.get_device_capability(0)}")
    print(f"📊 Número de GPUs: {torch.cuda.device_count()}")
    
    # Test simple
    print("\n🧪 Probando operación en GPU...")
    try:
        x = torch.rand(1000, 1000).cuda()
        y = torch.rand(1000, 1000).cuda()
        z = x @ y
        print("✅ Operación exitosa en GPU!")
    except Exception as e:
        print(f"❌ Error en operación GPU: {e}")
else:
    print("\n⚠️ CUDA NO está disponible")
    print("Posibles razones:")
    print("  1. No tienes GPU NVIDIA")
    print("  2. No tienes drivers NVIDIA instalados")
    print("  3. PyTorch instalado sin soporte CUDA")
    print("\n💡 Para instalar PyTorch con CUDA:")
    print("   pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")

print("\n" + "=" * 60)

# Verificar EasyOCR
print("\n🔍 Verificando EasyOCR...")
try:
    import easyocr
    print("✅ EasyOCR instalado")
    
    # Verificar si puede usar GPU
    reader = easyocr.Reader(['en'], gpu=cuda_available, verbose=False)
    print(f"✅ EasyOCR configurado con GPU: {cuda_available}")
except Exception as e:
    print(f"⚠️ Error con EasyOCR: {e}")

print("=" * 60)
