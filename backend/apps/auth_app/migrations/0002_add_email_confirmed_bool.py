# Generated migration to add emailConfirmed as BooleanField
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth_app", "0001_initial"),
    ]

    operations = [
        # Step 1: Add new BooleanField with different name
        migrations.AddField(
            model_name="user",
            name="email_confirmed_bool",
            field=models.BooleanField(default=False),
        ),
    ]
