# Generated migration to migrate data and remove old field
from django.db import migrations, models


def migrate_email_confirmed_data(apps, schema_editor):
    """Convert old emailConfirmed EmailField to new Boolean field"""
    User = apps.get_model("auth_app", "User")

    # Set all existing users as confirmed (they were created before this change)
    User.objects.all().update(email_confirmed_bool=True)


class Migration(migrations.Migration):

    dependencies = [
        ("auth_app", "0002_add_email_confirmed_bool"),
    ]

    operations = [
        # Step 2: Migrate data
        migrations.RunPython(migrate_email_confirmed_data, migrations.RunPython.noop),
        # Step 3: Remove old field
        migrations.RemoveField(
            model_name="user",
            name="emailConfirmed",
        ),
        # Step 4: Rename new field to original name
        migrations.RenameField(
            model_name="user",
            old_name="email_confirmed_bool",
            new_name="emailConfirmed",
        ),
    ]
