# Generated migration to add 'nivel' field with English values and set existing rows to 'medium'
from django.db import migrations, models


def set_existing_to_medium(apps, schema_editor):
    Denuncia = apps.get_model("vehicles", "Denuncia")
    Denuncia.objects.filter(nivel__isnull=True).update(nivel="medium")


class Migration(migrations.Migration):

    dependencies = [
        ("vehicles", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="denuncia",
            name="nivel",
            field=models.CharField(
                choices=[("low", "low"), ("medium", "medium"), ("high", "high")],
                default="medium",
                max_length=16,
            ),
            preserve_default=False,
        ),
        migrations.RunPython(
            set_existing_to_medium, reverse_code=migrations.RunPython.noop
        ),
    ]
