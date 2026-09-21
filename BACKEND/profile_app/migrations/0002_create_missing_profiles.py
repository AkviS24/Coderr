from django.db import migrations


def create_missing_profiles(apps, schema_editor):
    """Create profiles for users that do not have one."""
    User = apps.get_model('auth_app', 'CustomUser')
    UserProfile = apps.get_model('profile_app', 'UserProfile')

    existing_users = UserProfile.objects.values_list('user_id', flat=True)
    missing_users = User.objects.exclude(id__in=existing_users)
    UserProfile.objects.bulk_create(
        [UserProfile(user=user) for user in missing_users],
    )


class Migration(migrations.Migration):
    """Create profiles for existing users without profiles."""

    dependencies = [
        ('profile_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_missing_profiles,
            migrations.RunPython.noop,
        ),
    ]
