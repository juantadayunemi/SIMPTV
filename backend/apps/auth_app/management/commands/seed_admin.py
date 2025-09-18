from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from apps.auth_app.models import User, UserRole
from apps.entities.constants.roles import USER_ROLES_CHOICES
from django.utils import timezone


class Command(BaseCommand):
    help = "Crear usuario administrador por defecto: admin@gmail.com / 123"

    def handle(self, *args, **options):
        email = "admin@gmail.com"
        password = "123"

        # Verificar si ya existe
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"Usuario {email} ya existe."))
            return

        # Crear usuario administrador
        user = User.objects.create(
            email=email,
            passwordHash=make_password(password),
            fullName="Administrador Sistema",
            phoneNumber="+593999999999",
            isActive=True,
            emailConfirmed=True,  # Pre-verificado
            # createdAt y updatedAt se llenan automáticamente con auto_now_add/auto_now
        )

        # Crear rol de administrador
        admin_role = "ADMIN"  # Debe coincidir con USER_ROLES_CHOICES
        UserRole.objects.create(
            user=user,
            userId=str(user.id),
            role=admin_role,
            assignedBy="SYSTEM",
            isActive=True,
            # assignedAt, created_at, updated_at se llenan automáticamente
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"""
✅ Usuario administrador creado exitosamente:

📧 Email: {email}  
🔑 Password: {password}
👤 Nombre: {user.fullName}
📱 Teléfono: {user.phoneNumber}
🏷️  Rol: {admin_role}
✅ Activo: {user.isActive}
✅ Email Confirmado: {user.emailConfirmed}

🌐 Prueba el login en:
POST http://localhost:8000/api/auth/login/

Body:
{{
    "email": "{email}",
    "password": "{password}"
}}
            """
            )
        )
