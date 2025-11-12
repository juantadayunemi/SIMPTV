from django.db import migrations, models


def uppercase_severity(apps, schema_editor):
    Denuncia = apps.get_model("vehicles", "Denuncia")
    # After rename the field will be 'severidad'. Update values to uppercase equivalents.
    mapping = {"low": "LOW", "medium": "MEDIUM", "high": "HIGH"}
    for d in Denuncia.objects.all():
        val = getattr(d, "severidad", None)
        if val is None:
            d.severidad = "MEDIUM"
        else:
            d.severidad = mapping.get(val, val.upper())
        d.save(update_fields=["severidad"])


class Migration(migrations.Migration):

    dependencies = [
        ("vehicles", "0002_add_nivel"),
    ]

    operations = [
        migrations.RenameField(
            model_name="denuncia",
            old_name="nivel",
            new_name="severidad",
        ),
        migrations.RunPython(
            uppercase_severity, reverse_code=migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name="denuncia",
            name="severidad",
            field=models.CharField(
                choices=[("LOW", "LOW"), ("MEDIUM", "MEDIUM"), ("HIGH", "HIGH")],
                default="MEDIUM",
                max_length=16,
            ),
        ),
    ]
