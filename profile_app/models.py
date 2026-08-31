from django.db import models
from auth_app.models import CustomUser

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
    )

    file = models.FileField(
        upload_to='profile_pictures/',
        blank=True,
    )

    location = models.CharField(max_length=100, blank=True, default="")

    tel = models.CharField(max_length=25, blank=True, default="")

    description = models.TextField(max_length=1000, blank=True, default="")

    working_hours = models.CharField(max_length=25, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)