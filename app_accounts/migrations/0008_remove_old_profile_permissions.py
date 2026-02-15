from django.db import migrations


def remove_old_profile_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    Permission.objects.filter(
        codename__in=[
            "view_my_profile",
            "edit_my_profile",
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("app_accounts", "0007_alter_profile_options"),
    ]

    operations = [
        migrations.RunPython(remove_old_profile_permissions),
    ]
