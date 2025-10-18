from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.notifications_app.models import FCMDevice
from utils.fcm_service import FCMService
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = "Test FCM notifications by sending to all registered devices"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=str,
            help="Username to send notification to (default: all admin users)",
        )
        parser.add_argument(
            "--title",
            type=str,
            default="Notificación de Prueba",
            help="Notification title",
        )
        parser.add_argument(
            "--body",
            type=str,
            default="Esta es una notificación de prueba del sistema TrafiSmart",
            help="Notification body",
        )

    def handle(self, *args, **options):
        username = options["user"]
        title = options["title"]
        body = options["body"]

        if username:
            try:
                user = User.objects.get(username=username)
                users = [user]
            except User.DoesNotExist:
                self.stderr.write(f"User '{username}' not found")
                return
        else:
            # Send to all admin users
            users = User.objects.filter(is_staff=True)
            if not users.exists():
                self.stderr.write("No admin users found. Create an admin user first.")
                return

        self.stdout.write(
            "Sending test notification to {} user(s)".format(users.count())
        )

        total_devices = 0
        total_success = 0
        total_failure = 0

        for user in users:
            devices = FCMDevice.objects.filter(user=user, is_active=True)
            if not devices.exists():
                self.stdout.write(f"  User {user.username}: No active devices")
                continue

            tokens = list(devices.values_list("token", flat=True))
            self.stdout.write(f"  User {user.username}: {len(tokens)} device(s)")

            # Send notification
            result = FCMService.send_notification_to_multiple_tokens(
                tokens=tokens,
                title=title,
                body=body,
                data={"type": "test", "source": "management_command"},
            )

            total_devices += len(tokens)
            total_success += result["success"]
            total_failure += result["failure"]

            self.stdout.write(
                f"    Success: {result['success']}, Failure: {result['failure']}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal: {total_devices} devices, {total_success} success, {total_failure} failures"
            )
        )
