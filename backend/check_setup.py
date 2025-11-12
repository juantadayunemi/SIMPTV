"""
Quick Check Script - Verify IP Camera Setup
Verifica que todas las dependencias estén instaladas
"""
import sys

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'ultralytics': 'ultralytics'
    }
    
    missing = []
    
    print("🔍 Verificando dependencias...\n")
    
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - NO INSTALADO")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️ Faltan {len(missing)} paquete(s):")
        print("\nPara instalar, ejecuta:")
        print(f"pip install {' '.join(missing)}")
        return False
    else:
        print("\n✅ Todas las dependencias están instaladas!")
        return True

def check_ip_camera_config():
    """Check IP camera configuration"""
    print("\n📱 Verificando configuración de cámaras IP...\n")
    
    try:
        from config.ip_cameras import get_enabled_ip_cameras
        
        cameras = get_enabled_ip_cameras()
        
        if not cameras:
            print("⚠️ No hay cámaras IP habilitadas")
            print("   Edita: backend/config/ip_cameras.py")
            return False
        
        print(f"✅ {len(cameras)} cámara(s) IP configurada(s):\n")
        for cam in cameras:
            print(f"  • {cam['name']}")
            print(f"    URL: {cam['url']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 VERIFICACIÓN DE CONFIGURACIÓN - IP CAMERA")
    print("=" * 60)
    print()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check IP camera config
    config_ok = check_ip_camera_config()
    
    print("=" * 60)
    
    if deps_ok and config_ok:
        print("✅ TODO LISTO!")
        print("\nPuedes ejecutar:")
        print("  python test_ip_webcam.py")
        print()
        return 0
    else:
        print("⚠️ Hay problemas que resolver")
        return 1

if __name__ == "__main__":
    sys.exit(main())
