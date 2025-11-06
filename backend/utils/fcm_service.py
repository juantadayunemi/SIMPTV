"""
FCM Service - Updated to use Firebase Cloud Messaging API V1
"""

import logging
from typing import List, Dict, Any, Optional
from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError

logger = logging.getLogger(__name__)


class FCMService:
    """Service for sending Firebase Cloud Messaging notifications."""

    @staticmethod
    def send_notification(
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None,
    ) -> Dict[str, int]:
        """
        Send a notification to multiple devices using FCM API V1.

        Args:
            tokens: List of FCM device tokens
            title: Notification title
            body: Notification body
            data: Optional data payload (all values must be strings)
            image_url: Optional image URL for the notification

        Returns:
            Dictionary with 'success' and 'failure' counts
        """
        logger.info(f"🚀 [FCM SERVICE STEP 1] send_notification() iniciado")
        logger.info(f"   • Tokens recibidos: {len(tokens) if tokens else 0}")
        logger.info(f"   • Título: {title}")
        logger.info(f"   • Cuerpo: {body}")
        logger.info(f"   • Data: {data}")

        if not tokens:
            logger.warning("⚠️ [FCM SERVICE] No tokens provided for notification")
            return {"success": 0, "failure": 0}

        # Remove duplicates
        original_count = len(tokens)
        tokens = list(set(tokens))
        logger.info(
            f"🚀 [FCM SERVICE STEP 2] Tokens únicos: {len(tokens)} (original: {original_count})"
        )

        # Prepare notification
        logger.info(f"🚀 [FCM SERVICE STEP 3] Preparando objeto Notification...")
        notification = messaging.Notification(
            title=title,
            body=body,
            image=image_url if image_url else None,
        )
        logger.info(f"   ✅ Notification creada")

        # Prepare data payload (ensure all values are strings)
        if data:
            data = {k: str(v) for k, v in data.items()}
            logger.info(f"🚀 [FCM SERVICE STEP 4] Data payload convertida a strings")

        success_count = 0
        failure_count = 0

        logger.info(
            f"🚀 [FCM SERVICE STEP 5] ⚡ Iniciando envío a {len(tokens)} tokens..."
        )

        # Send to each token individually (more reliable than batch for now)
        for idx, token in enumerate(tokens, 1):
            logger.info(
                f"🚀 [FCM SERVICE] Enviando {idx}/{len(tokens)} - Token: {token[:20]}..."
            )
            try:
                message = messaging.Message(
                    notification=notification,
                    data=data,
                    token=token,
                    android=messaging.AndroidConfig(
                        priority="high",
                        notification=messaging.AndroidNotification(
                            sound="default",
                            channel_id="high_importance_channel",
                        ),
                    ),
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                sound="default",
                                badge=1,
                            )
                        )
                    ),
                    webpush=messaging.WebpushConfig(
                        notification=messaging.WebpushNotification(
                            icon="/icon-192x192.png",
                            badge="/badge-72x72.png",
                        )
                    ),
                )

                logger.info(f"   📤 Llamando a messaging.send()...")
                response = messaging.send(message)
                logger.info(f"   ✅ SUCCESS! Response: {response}")
                logger.info(f"   ✅ Successfully sent message: {response}")
                success_count += 1

            except FirebaseError as e:
                logger.error(f"   ❌ FirebaseError para token {token[:10]}...: {e}")
                failure_count += 1
            except Exception as e:
                logger.error(f"   ❌ Unexpected error para token {token[:10]}...: {e}")
                failure_count += 1

        result = {"success": success_count, "failure": failure_count}
        logger.info(f"🚀 [FCM SERVICE STEP 6] ✅ COMPLETADO!")
        logger.info(f"   • Total enviados: {len(tokens)}")
        logger.info(f"   • Éxitos: {success_count}")
        logger.info(f"   • Fallos: {failure_count}")
        logger.info(f"🚀 [FCM SERVICE] Notification sending completed: {result}")

        return result

    @staticmethod
    def send_stolen_vehicle_alert(
        admin_tokens: List[str],
        vehicle_info: Dict[str, Any],
        camera_location: str,
        detection_time: str,
    ) -> Dict[str, int]:
        """
        Send stolen vehicle alert to admins.

        Args:
            admin_tokens: List of admin device tokens
            vehicle_info: Dictionary with vehicle information
            camera_location: Location where vehicle was detected
            detection_time: Time of detection

        Returns:
            Dictionary with success/failure counts
        """
        title = "🚨 Vehículo Robado Detectado"
        body = (
            f"Placa {vehicle_info.get('plate', 'N/A')} detectada en {camera_location}"
        )

        data = {
            "type": "stolen_vehicle",
            "plate": str(vehicle_info.get("plate", "")),
            "make": str(vehicle_info.get("make", "")),
            "model": str(vehicle_info.get("model", "")),
            "color": str(vehicle_info.get("color", "")),
            "location": str(camera_location),
            "time": str(detection_time),
        }

        return FCMService.send_notification(
            tokens=admin_tokens,
            title=title,
            body=body,
            data=data,
        )

    @staticmethod
    def send_traffic_violation_alert(
        admin_tokens: List[str],
        violation_type: str,
        vehicle_info: Dict[str, Any],
        camera_location: str,
        detection_time: str,
    ) -> Dict[str, int]:
        """
        Send traffic violation alert to admins.

        Args:
            admin_tokens: List of admin device tokens
            violation_type: Type of violation
            vehicle_info: Dictionary with vehicle information
            camera_location: Location where violation occurred
            detection_time: Time of detection

        Returns:
            Dictionary with success/failure counts
        """
        title = "⚠️ Infracción de Tránsito"
        body = f"{violation_type} - Placa {vehicle_info.get('plate', 'N/A')}"

        data = {
            "type": "traffic_violation",
            "violation_type": str(violation_type),
            "plate": str(vehicle_info.get("plate", "")),
            "make": str(vehicle_info.get("make", "")),
            "model": str(vehicle_info.get("model", "")),
            "location": str(camera_location),
            "time": str(detection_time),
        }

        return FCMService.send_notification(
            tokens=admin_tokens,
            title=title,
            body=body,
            data=data,
        )

    @staticmethod
    def send_payment_reminder(
        user_tokens: List[str],
        fine_amount: float,
        due_date: str,
        fine_id: str,
    ) -> Dict[str, int]:
        """
        Send payment reminder notification.

        Args:
            user_tokens: List of user device tokens
            fine_amount: Amount of the fine
            due_date: Payment due date
            fine_id: Fine identifier

        Returns:
            Dictionary with success/failure counts
        """
        title = "💳 Recordatorio de Pago"
        body = f"Tiene una multa pendiente de ${fine_amount:.2f}"

        data = {
            "type": "payment_reminder",
            "fine_id": str(fine_id),
            "amount": str(fine_amount),
            "due_date": str(due_date),
        }

        return FCMService.send_notification(
            tokens=user_tokens,
            title=title,
            body=body,
            data=data,
        )

    @staticmethod
    def send_test_notification(
        tokens: List[str],
        title: Optional[str] = None,
        body: Optional[str] = None,
    ) -> Dict[str, int]:
        """
        Send a test notification.

        Args:
            tokens: List of device tokens
            title: Optional custom title
            body: Optional custom body

        Returns:
            Dictionary with success/failure counts
        """
        default_title = "🔔 Notificación de Prueba"
        default_body = "Esta es una notificación de prueba de TrafiSmart"

        return FCMService.send_notification(
            tokens=tokens,
            title=title or default_title,
            body=body or default_body,
            data={"type": "test"},
        )

    @staticmethod
    @staticmethod
    def send_vehicle_complaint_alert(
        admin_tokens: List[str],
        plate_number: str,
        owner_name: str,
        complaints_count: int,
        severity: str,
        camera_location: str,
        detection_time: str,
        case_number: str = "N/A",
        grouping_info: dict | None = None,  # ✨ NUEVO: información de agrupamiento
    ) -> Dict[str, int]:
        """
        Send vehicle complaint/denuncia alert to admins.

        Args:
            admin_tokens: List of admin device tokens
            plate_number: License plate number
            owner_name: Vehicle owner name
            complaints_count: Number of complaints
            severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
            camera_location: Camera location where detected
            detection_time: Time of detection
            case_number: Case/expediente number
            grouping_info: Optional dict with grouped detection info

        Returns:
            Dictionary with success/failure counts
        """
        logger.info(
            f"🚨 [VEHICLE ALERT STEP 1] send_vehicle_complaint_alert() iniciado"
        )
        logger.info(f"   • Admin tokens: {len(admin_tokens) if admin_tokens else 0}")
        logger.info(f"   • Placa: {plate_number}")
        logger.info(f"   • Propietario: {owner_name}")
        logger.info(f"   • Denuncias: {complaints_count}")
        logger.info(f"   • Severidad: {severity}")
        logger.info(f"   • Ubicación: {camera_location}")
        logger.info(f"   • Expediente: {case_number}")
        if grouping_info:
            logger.info(
                f"   • Agrupamiento: {grouping_info.get('detection_count')} detecciones en {grouping_info.get('time_window_minutes')}min"
            )

        # Emoji segun severidad (sin tildes para evitar problemas)
        severity_emoji = {
            "NONE": "✅",
            "LOW": "⚠️",
            "MEDIUM": "🚨",
            "HIGH": "🔴",
            "CRITICAL": "🆘",
        }
        emoji = severity_emoji.get(severity, "🚨")

        # Sonido según severidad
        severity_sound = {
            "NONE": "default",
            "LOW": "default",
            "MEDIUM": "alert",
            "HIGH": "urgent",
            "CRITICAL": "alarm",
        }
        sound = severity_sound.get(severity, "default")

        # Modificar título y cuerpo si es notificación agrupada
        if grouping_info and grouping_info.get("is_grouped"):
            detection_count = grouping_info.get("detection_count", 0)
            time_window = grouping_info.get("time_window_minutes", 0)
            locations = grouping_info.get("locations", [])

            title = f"📍 {emoji} Placa {plate_number} Detectada Múltiples Veces"
            body = f"Placa {plate_number} detectada {detection_count} veces en últimos {time_window} minutos. {complaints_count} denuncia(s). Propietario: {owner_name}"

            if len(locations) > 1:
                body += f". Ubicaciones: {', '.join(locations)}"
        else:
            title = f"{emoji} Vehiculo con Denuncias Detectado"
            body = f"Placa {plate_number} tiene {complaints_count} denuncia(s). Propietario: {owner_name}"

        logger.info(f"🚨 [VEHICLE ALERT STEP 2] Mensaje preparado:")
        logger.info(f"   • Título: {title}")
        logger.info(f"   • Cuerpo: {body}")
        logger.info(f"   • Sonido: {sound}")
        logger.info(f"   • Agrupado: {'Sí' if grouping_info else 'No'}")

        data = {
            "type": "vehicle_complaint",
            "plate_number": str(plate_number),
            "owner_name": str(owner_name),
            "complaints_count": str(complaints_count),
            "severity": str(severity),
            "case_number": str(case_number),
            "location": str(camera_location),
            "time": str(detection_time),
            "sound": sound,
            "is_grouped": str(grouping_info is not None),  # ✨ NUEVO
        }

        # Agregar información de agrupamiento si existe
        if grouping_info:
            data.update(
                {
                    "detection_count": str(grouping_info.get("detection_count", 1)),
                    "time_window_minutes": str(
                        grouping_info.get("time_window_minutes", 0)
                    ),
                    "locations": ",".join(grouping_info.get("locations", [])),
                }
            )

        logger.info(f"🚨 [VEHICLE ALERT STEP 3] ⚡ Llamando a send_notification()...")

        result = FCMService.send_notification(
            tokens=admin_tokens,
            title=title,
            body=body,
            data=data,
        )

        logger.info(f"🚨 [VEHICLE ALERT STEP 4] ✅ Resultado: {result}")
        return result
