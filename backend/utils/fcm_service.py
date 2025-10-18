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
        if not tokens:
            logger.warning("No tokens provided for notification")
            return {"success": 0, "failure": 0}

        # Remove duplicates
        tokens = list(set(tokens))
        
        # Prepare notification
        notification = messaging.Notification(
            title=title,
            body=body,
            image=image_url if image_url else None,
        )

        # Prepare data payload (ensure all values are strings)
        if data:
            data = {k: str(v) for k, v in data.items()}

        success_count = 0
        failure_count = 0

        # Send to each token individually (more reliable than batch for now)
        for token in tokens:
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

                response = messaging.send(message)
                logger.info(f"Successfully sent message: {response}")
                success_count += 1

            except FirebaseError as e:
                logger.error(f"Error sending to token {token[:10]}...: {e}")
                failure_count += 1
            except Exception as e:
                logger.error(f"Unexpected error sending to token {token[:10]}...: {e}")
                failure_count += 1

        result = {"success": success_count, "failure": failure_count}
        logger.info(f"Notification sending completed: {result}")
        
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
        body = f"Placa {vehicle_info.get('plate', 'N/A')} detectada en {camera_location}"

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