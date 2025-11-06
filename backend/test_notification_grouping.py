"""
Script de testing para el sistema de agrupamiento inteligente de notificaciones.
Permite probar diferentes escenarios de detección múltiple.

USO:
    python manage.py shell < test_notification_grouping.py

    O desde Django shell:
    exec(open('test_notification_grouping.py').read())
"""

import time
from datetime import datetime
from utils.notification_grouping import NotificationGroupingService


def print_separator():
    print("\n" + "=" * 80 + "\n")


def test_scenario_1():
    """
    Escenario 1: Primera detección
    Resultado esperado: Enviar notificación
    """
    print("🧪 TEST 1: Primera detección de placa")
    print("-" * 40)

    plate = "TEST001"

    # Resetear para testing limpio
    NotificationGroupingService.reset_detection(plate)

    should_send, info = NotificationGroupingService.should_send_notification(
        plate_number=plate, camera_location="Cámara Norte", complaints_count=3
    )

    print(f"Placa: {plate}")
    print(f"¿Enviar notificación?: {should_send}")
    print(f"Información de agrupamiento: {info}")
    print(
        f"✅ RESULTADO: {'CORRECTO' if should_send and info is None else 'INCORRECTO'}"
    )

    # Ver estadísticas
    stats = NotificationGroupingService.get_detection_stats(plate)
    print(f"Estadísticas en cache: {stats}")
    if stats:
        print(f"  • Count: {stats['count']}, Locations: {stats['locations']}")


def test_scenario_2():
    """
    Escenario 2: Segunda detección (menos de 5 min)
    Resultado esperado: NO enviar (solo 2 detecciones, mínimo es 3)
    """
    print("🧪 TEST 2: Segunda detección (silenciar)")
    print("-" * 40)

    plate = "TEST002"

    # Resetear
    NotificationGroupingService.reset_detection(plate)

    # Primera detección
    should_send_1, info_1 = NotificationGroupingService.should_send_notification(
        plate_number=plate, camera_location="Cámara Norte", complaints_count=3
    )
    print(f"1ª detección - Enviar: {should_send_1}")

    time.sleep(1)  # Esperar 1 segundo

    # Segunda detección
    should_send_2, info_2 = NotificationGroupingService.should_send_notification(
        plate_number=plate, camera_location="Cámara Norte", complaints_count=3
    )

    print(f"2ª detección - Enviar: {should_send_2}")
    print(f"Información: {info_2}")
    print(
        f"✅ RESULTADO: {'CORRECTO' if not should_send_2 else 'INCORRECTO (debería silenciar)'}"
    )

    stats = NotificationGroupingService.get_detection_stats(plate)
    if stats:
        print(f"Estadísticas: Count={stats['count']}, Locations={stats['locations']}")


def test_scenario_3():
    """
    Escenario 3: Tercera detección (alcanza mínimo)
    Resultado esperado: Enviar notificación AGRUPADA
    """
    print("🧪 TEST 3: Tercera detección (notificación agrupada)")
    print("-" * 40)

    plate = "TEST003"

    # Resetear
    NotificationGroupingService.reset_detection(plate)

    # Tres detecciones seguidas
    for i in range(1, 4):
        should_send, info = NotificationGroupingService.should_send_notification(
            plate_number=plate, camera_location=f"Cámara {i}", complaints_count=5
        )
        print(f"{i}ª detección - Enviar: {should_send}, Agrupado: {info is not None}")

        if i < 3:
            time.sleep(1)

    # La tercera debe enviar notificación agrupada
    print(f"\nInformación de agrupamiento (3ª detección): {info}")

    if info:
        print(f"  • Detection count: {info.get('detection_count')}")
        print(f"  • Time window: {info.get('time_window_minutes')} minutos")
        print(f"  • Locations: {info.get('locations')}")
        print(f"  • Is grouped: {info.get('is_grouped')}")

    expected = should_send and info and info.get("is_grouped")
    print(f"✅ RESULTADO: {'CORRECTO' if expected else 'INCORRECTO'}")


def test_scenario_4():
    """
    Escenario 4: Cuarta detección (ya notificado)
    Resultado esperado: NO enviar (ya se envió la notificación agrupada)
    """
    print("🧪 TEST 4: Cuarta detección (silenciar después de agrupada)")
    print("-" * 40)

    plate = "TEST004"

    # Resetear
    NotificationGroupingService.reset_detection(plate)

    # Cuatro detecciones
    results = []
    for i in range(1, 5):
        should_send, info = NotificationGroupingService.should_send_notification(
            plate_number=plate, camera_location="Cámara Principal", complaints_count=2
        )
        results.append((i, should_send, info))
        print(f"{i}ª detección - Enviar: {should_send}")
        time.sleep(0.5)

    # Verificar: 1ª=Sí, 2ª=No, 3ª=Sí(agrupada), 4ª=No
    expected_pattern = [True, False, True, False]
    actual_pattern = [r[1] for r in results]

    print(f"\nPatrón esperado: {expected_pattern}")
    print(f"Patrón obtenido: {actual_pattern}")
    print(
        f"✅ RESULTADO: {'CORRECTO' if actual_pattern == expected_pattern else 'INCORRECTO'}"
    )


def test_scenario_5():
    """
    Escenario 5: Detección fuera de ventana de tiempo
    Resultado esperado: Resetear contador, enviar notificación normal
    """
    print("🧪 TEST 5: Detección fuera de ventana de tiempo (>5 min)")
    print("-" * 40)

    plate = "TEST005"

    # Resetear
    NotificationGroupingService.reset_detection(plate)

    # Primera detección
    should_send_1, info_1 = NotificationGroupingService.should_send_notification(
        plate_number=plate, camera_location="Cámara A", complaints_count=4
    )
    print(f"1ª detección - Enviar: {should_send_1}")

    # Simular paso del tiempo modificando el cache manualmente
    from django.core.cache import cache
    import json
    from datetime import timedelta

    cache_key = NotificationGroupingService._get_cache_key(plate)
    cached_data = cache.get(cache_key)
    data = json.loads(cached_data)

    # Modificar timestamp para simular 6 minutos atrás
    old_time = datetime.now() - timedelta(minutes=6)
    data["first_detection"] = old_time.isoformat()
    cache.set(cache_key, json.dumps(data), NotificationGroupingService.CACHE_TTL)

    # Segunda detección (debería resetear)
    should_send_2, info_2 = NotificationGroupingService.should_send_notification(
        plate_number=plate, camera_location="Cámara B", complaints_count=4
    )

    print(f"2ª detección (6 min después) - Enviar: {should_send_2}")
    print(f"Información: {info_2}")

    # Verificar que se reseteó (debe enviar y NO estar agrupado)
    stats = NotificationGroupingService.get_detection_stats(plate)
    if stats:
        print(f"Contador después de reset: {stats['count']}")
        expected = should_send_2 and info_2 is None and stats["count"] == 1
    else:
        expected = False

    print(
        f"✅ RESULTADO: {'CORRECTO (reseteó contador)' if expected else 'INCORRECTO'}"
    )


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "🚀 INICIANDO TESTS DE AGRUPAMIENTO INTELIGENTE " + "🚀")
    print("=" * 80)

    tests = [
        test_scenario_1,
        test_scenario_2,
        test_scenario_3,
        test_scenario_4,
        test_scenario_5,
    ]

    for i, test_func in enumerate(tests, 1):
        try:
            test_func()
        except Exception as e:
            print(f"❌ ERROR en test {i}: {e}")
            import traceback

            traceback.print_exc()

        if i < len(tests):
            print_separator()

    print("\n" + "=" * 80)
    print("✅ TESTS COMPLETADOS\n")


# Ejecutar tests
if __name__ == "__main__":
    run_all_tests()
else:
    # Si se ejecuta desde Django shell
    run_all_tests()
