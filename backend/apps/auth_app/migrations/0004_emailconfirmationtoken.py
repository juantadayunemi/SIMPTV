# Generated migration to create EmailConfirmationToken model
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth_app", "0003_migrate_email_confirmed"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmailConfirmationToken",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("token", models.CharField(max_length=100, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("is_used", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="confirmation_tokens",
                        to="auth_app.user",
                    ),
                ),
            ],
            options={
                "db_table": "auth_email_confirmation_tokens",
                "ordering": ["-created_at"],
            },
        ),
    ]
