from django.db import models

from auth_app.models import CustomUser

# Create your models here.
class Review(models.Model):
    reviewer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews_written',
    )
    business_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews_received',
    )
    rating = models.IntegerField()
    description = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.reviewer} - {self.business_user} ({self.rating}/5)'


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['reviewer', 'business_user'],
                name='unique_review_per_business',
            ),
        ]