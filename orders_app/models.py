from django.db import models

from auth_app.models import CustomUser

# Create your models here.
class Order(models.Model):
    customer_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='customer_orders',
    )
    business_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='business_orders',
    )
    title = models.CharField(
        max_length=50,
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
    status = models.CharField(
        max_length=11,
        choices=[
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order {self.id} - {self.title}'

    class Meta:
        ordering = ['-created_at']