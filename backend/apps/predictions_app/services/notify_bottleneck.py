from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from apps.traffic_app.models import Camera, Location
from django.shortcuts import get_object_or_404

from apps.predictions_app.models import (
    NotificationBottleNeck,
    NotificationBottleNeckLog,
    NotificationTask,
)
from apps.auth_app.models import User
from celery import shared_task
from datetime import datetime


@shared_task
def send_bottleneck_notification(
    user_id, location_id, camera_id, bottleneck_datetime, notifications_id
):
    """
    Notify the user about a bottleneck at the specified location and camera.
    This function should implement the logic to send a notification to the user.
    """
    user = get_object_or_404(User, pk=user_id)
    location = get_object_or_404(Location, pk=location_id)
    camera = get_object_or_404(Camera, pk=camera_id)
    # Algoritmo para enviar la notificacion. Acontinuación el algoritmo completo:
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5174")
    logo_url = getattr(settings, "LOGO_URL", f"{frontend_url}/static/logo/logo.png")
    email_from = getattr(settings, "EMAIL_FROM", settings.EMAIL_HOST_USER)
    subject = "Notificación de Embotellamiento"

    bottleneck_datetime_obj = datetime.strptime(
        bottleneck_datetime, "%Y-%m-%d %H:%M:%S"
    )
    formatted_time = bottleneck_datetime_obj.strftime("%H:%M")
    text_content = f"""
    Notificación de Embotellamiento
    Hola {user.firstName},
    Se ha detectado un embotellamiento en la ubicación {location.description} en la cámara {camera.name} a las {formatted_time}.
    Puedes ver más detalles del nivel del tráfico en el siguiente enlace:
    {frontend_url}/bottleneck
    Saludos,
    El equipo de TraffSmart
    """

    html_content = f""" 
    <html>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <img src="{logo_url}" alt="Logo" style="max-width: 150px;">
                </div>
                <h2 style="color: #333;">Notificación de Embotellamiento</h2>
                <p>Hola {user.firstName},</p>
                <p>Se ha detectado un embotellamiento en la ubicación <strong>{location.description}</strong> en la cámara <strong>{camera.name}</strong> a las <strong>{formatted_time}</strong>.</p>
                <p>Puedes ver más detalles del nivel del tráfico en el siguiente enlace:</p>
                <p><a href="{frontend_url}/bottleneck" style="color: #1a73e8;">Ver Detalles del Tráfico</a></p>
                <br>
                <p>Saludos,<br>El equipo de TraffSmart</p>
            </div>
        </body>
    </html>
    """
    try:
        email = EmailMultiAlternatives(
            subject=subject, body=text_content, from_email=email_from, to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        notifications = NotificationBottleNeck.objects.filter(
            id=notifications_id
        ).first()

        print(f"Notificación enviada a {user.email}")
        NotificationBottleNeckLog.objects.create(
            notificationBottleNeckId=notifications,
            sentAt=timezone.now(),
            message="Notificación enviada exitosamente.",
            wasSuccessful=True,
        )
        try:
            task = NotificationTask.objects.get(
                taskId=send_bottleneck_notification.request.id
            )
            task.isActive = False
            task.save()
        except NotificationTask.DoesNotExist:
            print(f"Tarea con id {notifications_id} no encontrada")
        return True

    except Exception as e:
        print(f"Error enviando email a {user.email}: {e}")
        # NotificationBottleNeckLog.objects.create(
        #     notificationBottleNeckId=notifications_id,
        #     sentAt=timezone.now(),
        #     message=f"Error enviando email: {e}",
        #     wasSuccessful=False,
        # )
        return False
