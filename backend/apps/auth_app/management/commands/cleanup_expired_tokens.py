from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.auth_app.models import EmailConfirmationToken


class Command(BaseCommand):
    help = "Elimina tokens de confirmación de email expirados"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra cuántos tokens se eliminarían sin eliminarlos realmente",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Get expired tokens
        expired_tokens = EmailConfirmationToken.objects.filter(
            expiresAt__lt=timezone.now()
        )

        count = expired_tokens.count()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"🔍 DRY RUN: Se eliminarían {count} tokens expirados"
                )
            )
            if count > 0:
                self.stdout.write("\n📋 Tokens que se eliminarían:")
                for token in expired_tokens[:10]:  # Mostrar solo los primeros 10
                    self.stdout.write(
                        f"   - Usuario: {token.user.email}, Expiró: {token.expiresAt}"
                    )
                if count > 10:
                    self.stdout.write(f"   ... y {count - 10} más")
        else:
            if count > 0:
                # Delete expired tokens
                deleted_count, _ = expired_tokens.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Se eliminaron {deleted_count} tokens expirados exitosamente"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS("✅ No hay tokens expirados para eliminar")
                )
