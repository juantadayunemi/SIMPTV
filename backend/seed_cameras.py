"""
Script para agregar cámaras de prueba con ubicaciones reales de Ecuador
Ejecutar: python seed_cameras.py
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.traffic_app.models import Camera, Location


def create_cameras():
    """Crear 7 cámaras adicionales para completar 10 en total"""

    cameras_data = [
        {
            "name": "Av. 9 de Octubre - Centro Guayaquil",
            "brand": "Hikvision",
            "model": "DS-2CD2085FWD-I",
            "resolution": "1920x1080",
            "fps": 30,
            "status": "ACTIVE",
            "location": {
                "latitude": -2.1975,
                "longitude": -79.8862,
                "description": "Av. 9 de Octubre y Malecón, Centro de Guayaquil",
                "address": "Av. 9 de Octubre, Centro, Guayaquil",
                "city": "Guayaquil",
                "province": "Guayas",
                "country": "Ecuador",
            },
        },
        {
            "name": "Av. Francisco de Orellana - Samborondón",
            "brand": "Dahua",
            "model": "IPC-HFW5831E-ZE",
            "resolution": "3840x2160",
            "fps": 30,
            "status": "ACTIVE",
            "location": {
                "latitude": -2.1447,
                "longitude": -79.8897,
                "description": "Av. Francisco de Orellana, Plaza Lagos",
                "address": "Av. Francisco de Orellana, Samborondón",
                "city": "Samborondón",
                "province": "Guayas",
                "country": "Ecuador",
            },
        },
        {
            "name": "Av. Carlos Julio Arosemena - Kennedy",
            "brand": "Axis",
            "model": "P3245-LVE",
            "resolution": "1920x1080",
            "fps": 25,
            "status": "ACTIVE",
            "location": {
                "latitude": -2.1584,
                "longitude": -79.8985,
                "description": "Av. Carlos Julio Arosemena y Av. del Bombero",
                "address": "Av. Carlos Julio Arosemena, Kennedy Norte",
                "city": "Guayaquil",
                "province": "Guayas",
                "country": "Ecuador",
            },
        },
        {
            "name": "Terminal Terrestre Guayaquil",
            "brand": "Hikvision",
            "model": "DS-2CD2155FWD-I",
            "resolution": "2560x1920",
            "fps": 30,
            "status": "ACTIVE",
            "location": {
                "latitude": -2.2238,
                "longitude": -79.8991,
                "description": "Terminal Terrestre, entrada principal",
                "address": "Av. Benjamin Rosales, Terminal Terrestre",
                "city": "Guayaquil",
                "province": "Guayas",
                "country": "Ecuador",
            },
        },
        {
            "name": "Aeropuerto José Joaquín de Olmedo",
            "brand": "Bosch",
            "model": "DINION IP 5000i",
            "resolution": "1920x1080",
            "fps": 30,
            "status": "ACTIVE",
            "location": {
                "latitude": -2.1574,
                "longitude": -79.8836,
                "description": "Aeropuerto Internacional, vía principal",
                "address": "Av. de las Américas, Aeropuerto",
                "city": "Guayaquil",
                "province": "Guayas",
                "country": "Ecuador",
            },
        },
        {
            "name": "Puente de la Unidad Nacional",
            "brand": "Samsung",
            "model": "QNO-8080R",
            "resolution": "3840x2160",
            "fps": 25,
            "status": "ACTIVE",
            "location": {
                "latitude": -2.2183,
                "longitude": -79.8892,
                "description": "Puente de la Unidad Nacional, acceso norte",
                "address": "Puente de la Unidad Nacional",
                "city": "Guayaquil",
                "province": "Guayas",
                "country": "Ecuador",
            },
        },
        {
            "name": "Malecón 2000 - Rotonda",
            "brand": "Hikvision",
            "model": "DS-2CD2743G0-IZS",
            "resolution": "2560x1440",
            "fps": 30,
            "status": "ACTIVE",
            "location": {
                "latitude": -2.1925,
                "longitude": -79.8840,
                "description": "Malecón 2000, zona de la Rotonda",
                "address": "Malecón Simón Bolívar, Centro",
                "city": "Guayaquil",
                "province": "Guayas",
                "country": "Ecuador",
            },
        },
    ]

    created_count = 0

    for cam_data in cameras_data:
        try:
            # Verificar si ya existe una cámara con ese nombre
            if Camera.objects.filter(name=cam_data["name"]).exists():
                print(f"⚠️  Cámara '{cam_data['name']}' ya existe, omitiendo...")
                continue

            # Crear ubicación
            location_str = (
                f"{cam_data['location']['description']}, "
                f"{cam_data['location']['city']}, "
                f"{cam_data['location']['province']}, "
                f"{cam_data['location']['country']} "
                f"({cam_data['location']['city']}, {cam_data['location']['country']})"
            )

            # Crear cámara
            camera = Camera.objects.create(
                name=cam_data["name"],
                brand=cam_data["brand"],
                model=cam_data["model"],
                resolution=cam_data["resolution"],
                fps=cam_data["fps"],
                status=cam_data["status"],
                locationId=location_str,
            )

            # Crear ubicación en tabla Location
            Location.objects.create(
                locationId=location_str,
                latitude=cam_data["location"]["latitude"],
                longitude=cam_data["location"]["longitude"],
                description=cam_data["location"]["description"],
                address=cam_data["location"]["address"],
                city=cam_data["location"]["city"],
                province=cam_data["location"]["province"],
                country=cam_data["location"]["country"],
            )

            created_count += 1
            print(f"✅ Cámara creada: {camera.name}")
            print(f"   - Ubicación: {cam_data['location']['description']}")
            print(
                f"   - Coordenadas: {cam_data['location']['latitude']}, {cam_data['location']['longitude']}"
            )

        except Exception as e:
            print(f"❌ Error creando cámara '{cam_data['name']}': {str(e)}")

    print(f"\n{'='*70}")
    print(f"✅ Proceso completado: {created_count} cámaras creadas")
    print(f"{'='*70}")

    # Mostrar total de cámaras
    total_cameras = Camera.objects.count()
    print(f"\n📊 Total de cámaras en el sistema: {total_cameras}")

    # Listar todas las cámaras
    print("\n📋 Cámaras disponibles:")
    for i, cam in enumerate(Camera.objects.all(), 1):
        print(f"   {i}. {cam.name} ({cam.status})")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎥 CREACIÓN DE CÁMARAS DE PRUEBA")
    print("=" * 70 + "\n")

    create_cameras()

    print("\n🗺️  Ahora puedes ver las 10 cámaras en el mapa!")
    print("   Ejecuta el frontend y navega a la página principal.\n")
