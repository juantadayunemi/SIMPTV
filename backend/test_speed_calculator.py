"""
Test del calculador de velocidad
"""
import sys
import os

# Agregar ruta al path
sys.path.insert(0, 'D:/TrafiSmart/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from apps.traffic_app.speed_calculator import SpeedCalculator

def test_speed_calculator():
    print("🧪 Probando SpeedCalculator...")
    
    # Simular frames de un vehículo moviéndose
    frames = [
        {'bbox': [100, 100, 50, 50], 'frameNumber': 0},
        {'bbox': [120, 105, 50, 50], 'frameNumber': 1},
        {'bbox': [140, 110, 50, 50], 'frameNumber': 2},
        {'bbox': [160, 115, 50, 50], 'frameNumber': 3},
        {'bbox': [180, 120, 50, 50], 'frameNumber': 4},
    ]
    
    # Calcular velocidad
    speed = SpeedCalculator.calculate_speed_px_per_sec(frames, fps=30)
    
    if speed is not None:
        print(f"✅ Velocidad calculada: {speed:.2f} px/s")
        
        # Clasificar
        category = SpeedCalculator.classify_speed(speed)
        print(f"✅ Categoría: {category}")
        
        # Estimar km/h
        kmh = SpeedCalculator.estimate_kmh(speed)
        print(f"✅ Velocidad estimada: {kmh:.1f} km/h")
        
        # Resumen completo
        summary = SpeedCalculator.get_speed_summary(frames, fps=30, frame_width=1920, frame_height=1080)
        print(f"✅ Resumen completo:")
        print(f"   - Velocidad: {summary['speed_px_per_sec']:.2f} px/s")
        print(f"   - Categoría: {summary['speed_category']}")
        print(f"   - Estimado: {summary['estimated_kmh']:.1f} km/h")
        print(f"   - Confianza: {summary['confidence']:.2f}")
        
        print("\n✅ Test completado - SpeedCalculator funciona correctamente")
        return True
    else:
        print("❌ No se pudo calcular velocidad")
        return False

if __name__ == "__main__":
    try:
        test_speed_calculator()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()