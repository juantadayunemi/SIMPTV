from config.celery import app
from django.core.management.base import BaseCommand
from apps.notifications_app.models import NotificationTask, NotificationBottleNeck
        
class Command(BaseCommand):
    help = "Revoca las tareas de notificaciones programadas para embotellamientos que ya no están activas."

    def handle(self, *args, **kwargs):
        

        active_notifications = NotificationBottleNeck.objects.filter(isActive=True)

        for notification in active_notifications:
            scheduled_tasks = NotificationTask.objects.filter(
                notificationBottleNeckId=notification
            )
            for task in scheduled_tasks:
                app.control.revoke(task.taskId, terminate=True)
            
            scheduled_tasks.update(isActive=False)

        self.stdout.write(self.style.SUCCESS("Tareas de notificaciones revocadas correctamente."))