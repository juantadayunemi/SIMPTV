"""
Management command to cleanup unverified users after 4 minutes of registration

Usage:
    python manage.py cleanup_unverified_users

This command should be run periodically (via Celery beat or cron) to remove
users who registered but never confirmed their email within 4 minutes.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.auth_app.models import User


class Command(BaseCommand):
    help = "Elimina usuarios no verificados después de 4 minutos del registro"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simular la eliminación sin borrar realmente",
        )
        parser.add_argument(
            "--minutes",
            type=int,
            default=4,
            help="Minutos después del registro para eliminar (default: 4)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        minutes = options["minutes"]

        # Calculate cutoff time
        cutoff_time = timezone.now() - timedelta(minutes=minutes)

        # Find unverified users older than cutoff time
        unverified_users = User.objects.filter(
            emailConfirmed=False, createdAt__lt=cutoff_time
        )

        count = unverified_users.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS("✓ No hay usuarios no verificados para eliminar.")
            )
            return

        # Show users that will be deleted
        self.stdout.write(
            self.style.WARNING(f"\n📋 Usuarios no verificados encontrados: {count}")
        )

        for user in unverified_users:
            minutes_elapsed = int(
                (timezone.now() - user.createdAt).total_seconds() / 60
            )
            self.stdout.write(
                f"  - {user.email} (Registrado hace {minutes_elapsed} minutos)"
            )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  DRY RUN: No se eliminaron usuarios (use sin --dry-run para eliminar)"
                )
            )
            return

        # Delete unverified users
        deleted_count, _ = unverified_users.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Eliminados {deleted_count} usuarios no verificados."
            )
        )
