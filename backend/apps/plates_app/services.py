"""
Servicios para manejo de placas detectadas
"""

import logging
import os
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.conf import settings

from .models import DetectedPlate, DetectedPlateImage

logger = logging.getLogger(__name__)


def convert_to_relative_media_path(absolute_path):
    """
    Convierte ruta absoluta a relativa desde MEDIA_ROOT.

    Ejemplos:
        D:\\TrafiSmart\\backend\\media\\ROI YOLO\\file.jpg -> ROI YOLO/file.jpg
        /home/user/backend/media/Placas/file.jpg -> Placas/file.jpg

    Args:
        absolute_path: Ruta absoluta del archivo

    Returns:
        str: Ruta relativa desde media/ o la original si no es dentro de MEDIA_ROOT
    """
    if not absolute_path:
        return absolute_path

    # Obtener MEDIA_ROOT desde settings
    media_root = str(settings.MEDIA_ROOT)

    # Normalizar separadores a /
    absolute_path = os.path.normpath(absolute_path).replace("\\", "/")
    media_root = os.path.normpath(media_root).replace("\\", "/")

    # Si la ruta comienza con MEDIA_ROOT, quitarlo
    if absolute_path.startswith(media_root):
        # Quitar MEDIA_ROOT y el separador inicial
        relative_path = absolute_path[len(media_root) :].lstrip("/")
        return relative_path

    # Si no está dentro de MEDIA_ROOT, devolver tal cual (no deberíamos llegar aquí)
    logger.warning(f"⚠️ Ruta no está dentro de MEDIA_ROOT: {absolute_path}")
    return absolute_path


def save_detected_plate_to_db(plate_data, analysis, vehicle=None):
    """
    Guarda una placa detectada en la base de datos

    Args:
        plate_data (dict): Datos de la placa desde plate_service.process_vehicle_detection()
            - vehicle_id: ID del vehículo
            - plate_number: Texto de la placa detectada
            - confidence: Confianza de la detección (0.0 a 1.0)
            - detection_method: Método usado (ej: "triple", "roboflow", etc)
            - plate_image_path: Ruta de imagen de placa ROI
            - vehicle_image_path: Ruta de imagen de vehículo completo
            - timestamp (opcional): Timestamp de detección
        analysis: Instancia de TrafficAnalysis
        vehicle: Instancia de Vehicle (OPCIONAL - puede ser None para guardar inmediatamente)

    Returns:
        DetectedPlate: Instancia guardada o None si falla
    """
    if not plate_data:
        logger.warning("⚠️ plate_data es None, saltando guardado")
        return None

    # ⚠️ CAMBIO: vehicle puede ser None (se actualiza después)
    # Verificar que vehicle tiene ID si se proporciona
    if vehicle and not vehicle.id:
        logger.error(f"❌ Vehicle proporcionado no tiene ID: {vehicle}")
        return None

    # Verificar que la placa es válida (no es error/no detectada)
    plate_number = plate_data.get("plate_number", "")
    if plate_number in ["NOT_DETECTED", "NO_OCR", "ERROR", "UNREADABLE", ""]:
        logger.debug(f"⏭️ Placa no válida para guardar: {plate_number}")
        return None

    try:
        with transaction.atomic():
            # Calcular frameQuality basado en confianza
            confidence = plate_data.get("confidence", 0.0)
            frame_quality = min(confidence, 1.0)  # Normalizar a 0-1

            # Determinar método de detección
            detection_method = plate_data.get("detection_method", "unknown")

            # Timestamp de detección
            detected_at = plate_data.get("timestamp") or timezone.now()
            if isinstance(detected_at, str):
                detected_at = timezone.now()  # Si es string, usar ahora

            # Crear DetectedPlate
            detected_plate = DetectedPlate.objects.create(
                trafficAnalysisId=analysis,
                vehicleId=vehicle,
                plateNumber=plate_number[:20],  # Max 20 chars según modelo
                confidence=Decimal(
                    str(confidence)
                ),  # DecimalField(5,4) - Django valida automáticamente
                detectionMethod=detection_method[:50],  # Max 50 chars
                frameNumber=0,  # No tenemos frame number exacto, estimado
                frameQuality=Decimal(
                    str(frame_quality)
                ),  # DecimalField(5,4) - Django valida automáticamente
                detectedAt=detected_at,
                wasCheckedForComplaints=False,  # Aún no se ha verificado
                hasComplaints=False,  # Default
            )

            logger.info(
                f"✅ DetectedPlate guardada: ID={detected_plate.id}, Placa={plate_number}, Vehicle={vehicle.id if vehicle else 'NULL (temporal)'}"
            )

            # Guardar imágenes asociadas
            images_created = 0

            # 1. Imagen del vehículo completo (ROI YOLO)
            vehicle_image_path = plate_data.get("vehicle_image_path")
            if vehicle_image_path and os.path.exists(vehicle_image_path):
                try:
                    # Convertir a ruta relativa desde media/
                    relative_path = convert_to_relative_media_path(vehicle_image_path)
                    file_size = os.path.getsize(vehicle_image_path)

                    DetectedPlateImage.objects.create(
                        detectedPlateId=detected_plate,
                        localImagePath=relative_path[:500],  # Max 500 chars
                        imageType="VEHICLE_FULL",
                        frameNumber=0,
                        capturedAt=detected_at,
                        fileSize=file_size,
                        resolution=None,  # Opcional, no lo calculamos por performance
                    )
                    images_created += 1
                    logger.debug(f"  📷 VEHICLE_FULL guardada: {relative_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Error guardando VEHICLE_FULL image: {e}")

            # 2. Imagen de la placa (ROI de placa)
            plate_image_path = plate_data.get("plate_image_path")
            if plate_image_path and os.path.exists(plate_image_path):
                try:
                    # Convertir a ruta relativa desde media/
                    relative_path = convert_to_relative_media_path(plate_image_path)
                    file_size = os.path.getsize(plate_image_path)

                    DetectedPlateImage.objects.create(
                        detectedPlateId=detected_plate,
                        localImagePath=relative_path[:500],
                        imageType="PLATE_ROI",
                        frameNumber=0,
                        capturedAt=detected_at,
                        fileSize=file_size,
                        resolution=None,
                    )
                    images_created += 1
                    logger.debug(f"  📷 PLATE_ROI guardada: {relative_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Error guardando PLATE_ROI image: {e}")

            logger.info(
                f"✅ {images_created} imágenes guardadas para placa {detected_plate.id}"
            )

            return detected_plate

    except Exception as e:
        logger.error(f"❌ Error guardando DetectedPlate en DB: {e}", exc_info=True)
        return None


def save_complaint_detection_to_db(detected_plate, api_response_data):
    """
    Guarda información de denuncia desde la API gubernamental en la base de datos.

    Args:
        detected_plate: Instancia de DetectedPlate (debe estar guardada en DB)
        api_response_data: Dict con datos de la API gubernamental:
            {
                'placa': 'ABC1234',
                'propietario': {'nombre': '...', 'cedula': '...'},
                'ubicacion': {'direccion': '...'},
                'expediente': '...',
                'denuncias': ['...', '...']
            }

    Returns:
        VehicleComplaintDetection: Instancia guardada o None si falla
    """
    from .models import VehicleComplaintDetection, VehicleComplaint

    if not detected_plate or not api_response_data:
        logger.warning(
            "⚠️ detected_plate o api_response_data es None, saltando guardado de denuncia"
        )
        return None

    # Verificar que detected_plate tiene ID
    if not detected_plate.id:
        logger.error(f"❌ DetectedPlate no tiene ID, no se puede guardar denuncia")
        return None

    try:
        with transaction.atomic():
            # Extraer datos del propietario
            propietario = api_response_data.get("propietario", {})
            owner_name = propietario.get("nombre", "DESCONOCIDO")[:200]
            owner_id_number = propietario.get("cedula", "N/A")[:32]

            # Extraer ubicación
            ubicacion = api_response_data.get("ubicacion", {})
            owner_address = ubicacion.get("direccion", "NO DISPONIBLE")[:400]

            # Extraer expediente
            case_number = api_response_data.get("expediente", "N/A")[:64]

            # Contar denuncias
            denuncias = api_response_data.get("denuncias", [])
            total_complaints = len(denuncias)

            # Determinar severidad basada en cantidad de denuncias
            if total_complaints == 0:
                severity = "NONE"
            elif total_complaints == 1:
                severity = "LOW"
            elif total_complaints <= 3:
                severity = "MEDIUM"
            elif total_complaints <= 5:
                severity = "HIGH"
            else:
                severity = "CRITICAL"

            # Crear VehicleComplaintDetection (header/resumen)
            complaint_detection = VehicleComplaintDetection.objects.create(
                detectedPlateId=detected_plate,
                ownerName=owner_name,
                ownerIdNumber=owner_id_number,
                ownerAddress=owner_address,
                caseNumber=case_number,
                totalComplaintsCount=total_complaints,
                severity=severity,
                wasNotified=False,  # Aún no se ha notificado
                notes=f"Detectado automáticamente desde API gubernamental",
            )

            logger.info(
                f"✅ VehicleComplaintDetection guardada: ID={complaint_detection.id}, "
                f"Placa={api_response_data.get('placa')}, Denuncias={total_complaints}, "
                f"Severidad={severity}"
            )

            # Crear registros individuales de denuncias
            complaints_created = 0
            for idx, complaint_text in enumerate(denuncias, start=1):
                if complaint_text and len(complaint_text.strip()) > 0:
                    VehicleComplaint.objects.create(
                        detectionId=complaint_detection,
                        complaintText=complaint_text[
                            :2000
                        ],  # TextField, pero limitamos
                        sequenceNumber=idx,
                        severity=severity,  # Heredar severidad del detection
                    )
                    complaints_created += 1

            logger.info(
                f"✅ {complaints_created} denuncias individuales guardadas para detección {complaint_detection.id}"
            )

            # Actualizar DetectedPlate para marcar que tiene denuncias
            detected_plate.hasComplaints = True
            detected_plate.wasCheckedForComplaints = True
            detected_plate.checkedAt = timezone.now()
            detected_plate.save(
                update_fields=["hasComplaints", "wasCheckedForComplaints", "checkedAt"]
            )

            return complaint_detection

    except Exception as e:
        logger.error(
            f"❌ Error guardando VehicleComplaintDetection en DB: {e}", exc_info=True
        )
        return None
