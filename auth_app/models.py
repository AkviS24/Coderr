from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Represent a Coderr user with a customer or business type."""

    TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('business', 'Business'),
    )

    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='customer',
    )