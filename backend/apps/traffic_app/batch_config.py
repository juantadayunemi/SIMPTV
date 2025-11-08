"""
⚙️ CONFIGURACIÓN RÁPIDA BATCH PROCESSING
Edita estos valores según tu hardware y necesidades
"""

# ============================================================
# 🎚️ PERFILES PREDEFINIDOS
# ============================================================

PROFILES = {
    "ultra_fast": {
        "BATCH_SIZE": 32,
        "IMGSZ": 416,
        "CONF_THRESHOLD": 0.6,
        "MAX_DETECTIONS": 30,
        "SKIP_FRAMES": 2,  # Analiza 1 de cada 2 frames
        "description": "Máxima velocidad, menor precisión",
    },
    "balanced": {
        "BATCH_SIZE": 16,
        "IMGSZ": 640,
        "CONF_THRESHOLD": 0.5,
        "MAX_DETECTIONS": 50,
        "SKIP_FRAMES": 1,  # Analiza todos los frames
        "description": "Balance entre velocidad y precisión (RECOMENDADO)",
    },
    "quality": {
        "BATCH_SIZE": 8,
        "IMGSZ": 640,
        "CONF_THRESHOLD": 0.4,
        "MAX_DETECTIONS": 80,
        "SKIP_FRAMES": 1,
        "description": "Máxima precisión, menor velocidad",
    },
    "low_vram": {
        "BATCH_SIZE": 8,
        "IMGSZ": 416,
        "CONF_THRESHOLD": 0.5,
        "MAX_DETECTIONS": 40,
        "SKIP_FRAMES": 1,
        "description": "Para GPUs con < 4GB VRAM",
    },
}

# ============================================================
# 🎯 PERFIL ACTIVO
# ============================================================
# Opciones: "ultra_fast", "balanced", "quality", "low_vram"

ACTIVE_PROFILE = "balanced"

# ============================================================
# 🔧 CONFIGURACIÓN PERSONALIZADA (Override)
# ============================================================
# Puedes sobrescribir valores del perfil aquí

CUSTOM_CONFIG = {
    # Descomenta para override:
    # "BATCH_SIZE": 20,
    # "IMGSZ": 480,
    # "CONF_THRESHOLD": 0.55,
    # "MAX_DETECTIONS": 45,
    # "SKIP_FRAMES": 1,
    # WebSocket streaming
    # "WS_BUFFER_SECONDS": 2.5,
    # "WS_SEND_BATCH_SIZE": 20,
    # Memoria
    # "MEMORY_CLEAR_INTERVAL": 80,
    # "DB_SAVE_BATCH_SIZE": 15,
}

# ============================================================
# 📊 OBTENER CONFIGURACIÓN FINAL
# ============================================================


def get_config():
    """Retorna configuración combinada"""
    base_config = PROFILES[ACTIVE_PROFILE].copy()
    base_config.update(CUSTOM_CONFIG)
    return base_config


# ============================================================
# 🖨️ MOSTRAR CONFIGURACIÓN
# ============================================================

if __name__ == "__main__":
    config = get_config()
    profile = PROFILES[ACTIVE_PROFILE]

    print("=" * 60)
    print("⚙️  CONFIGURACIÓN BATCH PROCESSING")
    print("=" * 60)
    print(f"\n📋 Perfil activo: {ACTIVE_PROFILE.upper()}")
    print(f"   {profile['description']}")
    print("\n🎚️  Parámetros:")
    print(f"   - Batch size:        {config.get('BATCH_SIZE', 16)}")
    print(f"   - Image size:        {config.get('IMGSZ', 640)}")
    print(f"   - Confidence:        {config.get('CONF_THRESHOLD', 0.5)}")
    print(f"   - Max detections:    {config.get('MAX_DETECTIONS', 50)}")
    print(f"   - Skip frames:       {config.get('SKIP_FRAMES', 1)}")
    print(f"   - WS buffer (s):     {config.get('WS_BUFFER_SECONDS', 2.0)}")
    print(f"   - WS batch size:     {config.get('WS_SEND_BATCH_SIZE', 15)}")
    print("\n💾 Memoria:")
    print(f"   - Clear interval:    {config.get('MEMORY_CLEAR_INTERVAL', 100)}")
    print(f"   - DB batch size:     {config.get('DB_SAVE_BATCH_SIZE', 20)}")
    print("\n" + "=" * 60 + "\n")

    # Recomendaciones
    print("💡 RECOMENDACIONES:")
    print()

    if config.get("BATCH_SIZE", 16) > 24:
        print("   ⚠️  Batch size alto (>24): Puede causar Out of Memory")
        print("      Solución: Reducir a 16-20 o bajar IMGSZ")
        print()

    if config.get("IMGSZ", 640) > 640:
        print("   ⚠️  Image size alto (>640): GPU más lenta")
        print("      Solución: Usar 640 o 416 para más velocidad")
        print()

    if config.get("SKIP_FRAMES", 1) > 1:
        print(f"   ℹ️  Skip frames activado ({config.get('SKIP_FRAMES')})")
        print(f"      Analizando 1 de cada {config.get('SKIP_FRAMES')} frames")
        print()

    if config.get("CONF_THRESHOLD", 0.5) < 0.4:
        print("   ⚠️  Confidence bajo (<0.4): Muchas detecciones falsas")
        print("      Solución: Aumentar a 0.5-0.6")
        print()

    print("✅ Configuración lista para usar")
    print()
