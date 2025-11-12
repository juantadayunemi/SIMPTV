from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count, Prefetch
from .models import FCMDevice, NotificationLog
from apps.plates_app.models import VehicleComplaintDetection, VehicleComplaint
from .serializers import (
    FCMDeviceListSerializer,
    RegisterFCMTokenSerializer,
    TestNotificationSerializer,
    NotificationLogSerializer,
    VehicleComplaintDetectionSerializer,
    VehicleComplaintDetectionDetailSerializer,
)
from utils.fcm_service import FCMService
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class FCMDeviceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing FCM devices."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FCMDevice.objects.filter(user=self.request.user, is_active=True)

    def get_serializer_class(self):
        if self.action == "list":
            return FCMDeviceListSerializer
        return FCMDeviceListSerializer  # Default to list serializer

    @action(detail=False, methods=["post"])
    def register_token(self, request):
        """Register or update FCM token for current user."""
        logger.info(
            f"📥 Registro de token FCM solicitado por usuario: {request.user.email if request.user.is_authenticated else 'Anonymous'}"
        )
        logger.info(f"📦 Datos recibidos: {request.data}")

        serializer = RegisterFCMTokenSerializer(data=request.data)
        if serializer.is_valid():
            try:
                logger.info(f"✅ Datos validados correctamente")
                device = serializer.create_device(request.user)
                logger.info(
                    f"✅ Dispositivo creado/actualizado: ID={device.id}, Token={device.token[:20]}..., Usuario={device.user.email}"
                )
                return Response(
                    {
                        "message": "Token registrado exitosamente",
                        "device_id": device.id,
                        "created": device.created_at == device.updated_at,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                logger.error(f"❌ Error registering FCM token: {e}", exc_info=True)
                return Response(
                    {"error": "Error al registrar el token"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        logger.error(f"❌ Errores de validación: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"])
    def deactivate(self, request, pk=None):
        """Deactivate FCM device (soft delete)."""
        try:
            device = self.get_object()
            device.is_active = False
            device.save()
            return Response({"message": "Dispositivo desactivado"})
        except Exception as e:
            logger.error(f"Error deactivating device: {e}")
            return Response(
                {"error": "Error al desactivar dispositivo"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for notification logs."""

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationLogSerializer
    # pagination_class = None  # Usar paginación por defecto (settings.py)

    def get_queryset(self):
        queryset = NotificationLog.objects.filter(user=self.request.user).order_by(
            "-sent_at"
        )

        # Filtro por búsqueda de placa
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(data__plate_number__icontains=search)

        # Filtro por severidad
        severity = self.request.query_params.get("severity", None)
        if severity:
            queryset = queryset.filter(data__severity=severity)

        # Filtro por tipo de notificación
        notification_type = self.request.query_params.get("type", None)
        if notification_type:
            queryset = queryset.filter(notificationType=notification_type)

        return queryset

    @action(detail=True, methods=["get"])
    def complaint_details(self, request, pk=None):
        """
        Obtener detalles completos de una denuncia vehicular desde una notificación.
        GET /api/notifications/notifications/{id}/complaint_details/
        """
        try:
            notification = self.get_object()

            # Verificar que la notificación tenga detected_plate_id
            detected_plate_id = notification.data.get("detected_plate_id")
            if not detected_plate_id:
                return Response(
                    {
                        "error": "Esta notificación no tiene información de placa detectada"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Obtener VehicleComplaintDetection
            try:
                complaint_detection = VehicleComplaintDetection.objects.select_related(
                    "detectedPlateId"
                ).get(detectedPlateId_id=detected_plate_id)
            except VehicleComplaintDetection.DoesNotExist:
                return Response(
                    {"error": "No se encontró la detección de denuncia"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Obtener todas las denuncias asociadas
            complaints = VehicleComplaint.objects.filter(
                detectionId=complaint_detection
            ).order_by("-createdAt")

            # Serializar datos
            detection_data = {
                "id": complaint_detection.id,
                "ownerName": complaint_detection.ownerName,
                "ownerIdNumber": complaint_detection.ownerIdNumber,
                "ownerAddress": complaint_detection.ownerAddress,
                "caseNumber": complaint_detection.caseNumber,
                "severity": complaint_detection.severity,
            }

            complaints_data = [
                {
                    "id": complaint.id,
                    "complaintText": complaint.complaintText,
                    "complaintType": complaint.complaintType,
                    "complaintDate": complaint.complaintDate,
                    "severity": complaint.severity,
                    "sequenceNumber": complaint.sequenceNumber,
                    "createdAt": complaint.createdAt,
                }
                for complaint in complaints
            ]

            return Response(
                {
                    "success": True,
                    "detection": detection_data,
                    "complaints": complaints_data,
                    "complaintsCount": len(complaints_data),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(
                f"❌ Error obteniendo detalles de denuncia: {e}", exc_info=True
            )
            return Response(
                {"error": f"Error al obtener detalles: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def send_test(self, request):
        """Send test notification to user's devices."""
        serializer = TestNotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        devices = FCMDevice.objects.filter(user=user, is_active=True)

        if not devices.exists():
            return Response(
                {
                    "error": "No hay dispositivos registrados para recibir notificaciones"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        tokens = list(devices.values_list("token", flat=True))
        title = serializer.validated_data.get("title", "Notificación de Prueba")
        body = serializer.validated_data.get(
            "body", "Esta es una notificación de prueba del sistema TrafiSmart"
        )

        # Send notification
        result = FCMService.send_notification_to_multiple_tokens(
            tokens=tokens, title=title, body=body, data={"type": "test"}
        )

        # Log the notification
        for device in devices:
            NotificationLog.objects.create(
                user=user,
                notification_type="test",
                title=title,
                body=body,
                data={"type": "test"},
                fcm_response=result,
                success=result["success"] > 0,
            )
            device.mark_as_used()

        return Response(
            {
                "message": "Notificación de prueba enviada",
                "result": result,
                "devices_count": len(tokens),
            }
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_stolen_vehicle_alert(request):
    """
    Send alert for detected stolen vehicle.
    This endpoint can be called by the traffic analysis system.
    """
    try:
        # Get admin users by role
        from apps.auth_app.models import UserRole

        admin_roles = UserRole.objects.filter(role="ADMIN")
        admin_user_ids = admin_roles.values_list("user_id", flat=True).distinct()
        admin_users = User.objects.filter(id__in=admin_user_ids)

        if not admin_users.exists():
            return Response(
                {"error": "No hay usuarios administradores configurados"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extract vehicle and detection info from request
        vehicle_info = request.data.get("vehicle_info", {})
        camera_location = request.data.get("camera_location", "Ubicación desconocida")
        detection_time = request.data.get("detection_time", timezone.now().isoformat())

        # Collect all admin device tokens
        all_tokens = []
        for admin in admin_users:
            admin_devices = FCMDevice.objects.filter(user=admin, is_active=True)
            all_tokens.extend(list(admin_devices.values_list("token", flat=True)))

        if not all_tokens:
            return Response(
                {"error": "No hay dispositivos registrados para administradores"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Send alert
        result = FCMService.send_stolen_vehicle_alert(
            admin_tokens=all_tokens,
            vehicle_info=vehicle_info,
            camera_location=camera_location,
            detection_time=detection_time,
        )

        # Log notifications for each admin
        for admin in admin_users:
            admin_devices = FCMDevice.objects.filter(user=admin, is_active=True)
            for device in admin_devices:
                NotificationLog.objects.create(
                    user=admin,
                    notification_type="stolen_vehicle",
                    title="🚨 VEHÍCULO ROBADO DETECTADO",
                    body=f"Placa: {vehicle_info.get('plate', 'N/A')} - Ubicación: {camera_location}",
                    data={
                        "type": "stolen_vehicle_alert",
                        "plate": vehicle_info.get("plate", ""),
                        "camera_location": camera_location,
                        "detection_time": detection_time,
                    },
                    fcm_response=result,
                    success=result["success"] > 0,
                )
                device.mark_as_used()

        return Response(
            {
                "message": "Alerta de vehículo robado enviada",
                "result": result,
                "admins_notified": admin_users.count(),
                "devices_notified": len(all_tokens),
            }
        )

    except Exception as e:
        logger.error(f"Error sending stolen vehicle alert: {e}")
        return Response(
            {"error": "Error interno del servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_traffic_violation_alert(request):
    """
    Send alert for traffic violation.
    This endpoint can be called by the traffic analysis system.
    """
    try:
        # Get admin users by role
        from apps.auth_app.models import UserRole

        admin_roles = UserRole.objects.filter(role="ADMIN")
        admin_user_ids = admin_roles.values_list("user_id", flat=True).distinct()
        admin_users = User.objects.filter(id__in=admin_user_ids)

        if not admin_users.exists():
            return Response(
                {"error": "No hay usuarios administradores configurados"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        violation_type = request.data.get("violation_type", "infracción")
        vehicle_info = request.data.get("vehicle_info", {})
        camera_location = request.data.get("camera_location", "Ubicación desconocida")
        detection_time = request.data.get("detection_time", timezone.now().isoformat())

        # Collect all admin device tokens
        all_tokens = []
        for admin in admin_users:
            admin_devices = FCMDevice.objects.filter(user=admin, is_active=True)
            all_tokens.extend(list(admin_devices.values_list("token", flat=True)))

        if not all_tokens:
            return Response(
                {"error": "No hay dispositivos registrados para administradores"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Send alert
        result = FCMService.send_traffic_violation_alert(
            admin_tokens=all_tokens,
            violation_type=violation_type,
            vehicle_info=vehicle_info,
            camera_location=camera_location,
            detection_time=detection_time,
        )

        # Log notifications
        for admin in admin_users:
            admin_devices = FCMDevice.objects.filter(user=admin, is_active=True)
            for device in admin_devices:
                NotificationLog.objects.create(
                    user=admin,
                    notification_type="traffic_violation",
                    title="⚠️ INFRACCIÓN DE TRÁNSITO DETECTADA",
                    body=f"{violation_type} - Placa: {vehicle_info.get('plate', 'N/A')} - {camera_location}",
                    data={
                        "type": "traffic_violation_alert",
                        "violation_type": violation_type,
                        "plate": vehicle_info.get("plate", ""),
                        "camera_location": camera_location,
                        "detection_time": detection_time,
                    },
                    fcm_response=result,
                    success=result["success"] > 0,
                )
                device.mark_as_used()

        return Response(
            {
                "message": "Alerta de infracción enviada",
                "result": result,
                "admins_notified": admin_users.count(),
                "devices_notified": len(all_tokens),
            }
        )

    except Exception as e:
        logger.error(f"Error sending traffic violation alert: {e}")
        return Response(
            {"error": "Error interno del servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class VehicleComplaintViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar vehículos con denuncias.
    Solo lectura (no permite crear/editar).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = VehicleComplaintDetectionSerializer

    def get_serializer_class(self):
        """Use detail serializer for retrieve action."""
        if self.action == "retrieve":
            return VehicleComplaintDetectionDetailSerializer
        return VehicleComplaintDetectionSerializer

    def get_queryset(self):
        queryset = (
            VehicleComplaintDetection.objects.select_related(
                "detectedPlateId", "detectedPlateId__vehicleId"
            )
            .prefetch_related(
                Prefetch(
                    "vehiclecomplaintentity_detection_set",
                    queryset=VehicleComplaint.objects.all().order_by("sequenceNumber"),
                )
            )
            .filter(isActive=True)
            .order_by("-createdAt")
        )

        # Filtro por búsqueda de placa
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(detectedPlateId__plateNumber__icontains=search)

        # Filtro por severidad
        severity = self.request.query_params.get("severity", None)
        if severity and severity != "all":
            queryset = queryset.filter(severity=severity.upper())

        # Filtro por estado de notificación
        notified = self.request.query_params.get("notified", None)
        if notified == "true":
            queryset = queryset.filter(wasNotified=True)
        elif notified == "false":
            queryset = queryset.filter(wasNotified=False)

        return queryset

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Obtener estadísticas de denuncias."""
        total = VehicleComplaintDetection.objects.filter(isActive=True).count()
        medium_priority = VehicleComplaintDetection.objects.filter(
            isActive=True, severity="MEDIUM"
        ).count()
        high_priority = VehicleComplaintDetection.objects.filter(
            isActive=True, severity="HIGH"
        ).count()
        today = timezone.now().date()
        today_alerts = VehicleComplaintDetection.objects.filter(
            isActive=True, createdAt__date=today
        ).count()

        return Response(
            {
                "totalComplaints": total,
                "mediumPriority": medium_priority,
                "highPriority": high_priority,
                "alertsToday": today_alerts,
            }
        )
