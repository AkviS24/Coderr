from django.db import models

from auth_app.models import CustomUser

# Create your models here.
class Offer(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='offers',
    )
    title = models.CharField(max_length=35)
    image = models.ImageField(
        upload_to='offer_images/',
        null=True,
        blank=True,
    )
    description = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



class OfferDetail(models.Model):
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        max_length=35,
    )
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    features = models.JSONField()
    offer_type = models.CharField(
        max_length=10,
        choices=[
            ('basic', 'Basic'),
            ('standard', 'Standard'),
            ('premium', 'Premium'),
        ],
    )

    def __str__(self):
        return self.title