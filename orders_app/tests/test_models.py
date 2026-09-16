from django.test import TestCase

from auth_app.models import CustomUser
from orders_app.models import Order


class OrderModelTest(TestCase):
    """Test Order model behavior."""

    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            username='customer',
            password='customerpassword123!',
            type='customer',
        )
        self.business = CustomUser.objects.create_user(
            username='business',
            password='businesspassword123!',
            type='business',
        )

    def _create_order(self, **kwargs):
        order_data = {
            'customer_user': self.customer,
            'business_user': self.business,
            'title': 'Test Order',
            'revisions': 3,
            'delivery_time_in_days': 7,
            'price': 100,
            'features': ['Logo Design'],
            'offer_type': 'basic',
            'status': 'in_progress',
        }
        order_data.update(kwargs)

        return Order.objects.create(**order_data)

    def test_order_str(self):
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title='Test Order',
            revisions=3,
            delivery_time_in_days=7,
            price=100.00,
            features=['Logo Design'],
            offer_type='basic',
            status='in_progress',
        )

        self.assertEqual(
            str(order),
            f'Order {order.id} - Test Order',
        )

    def test_order_users(self):
        order = self._create_order()

        self.assertEqual(
            order.customer_user,
            self.customer,
        )

        self.assertEqual(
            order.business_user,
            self.business,
        )

    def test_order_status(self):
        order1 = self._create_order(
            title='In Progress Test Order',
            status='in_progress',
        )
        order2 = self._create_order(
            title='Completed Test Order',
            status='completed',
        )
        order3 = self._create_order(
            title='Cancelled Test Order',
            status='cancelled',
        )

        self.assertEqual(
            order1.status,
            'in_progress',
        )

        self.assertEqual(
            order2.status,
            'completed',
        )

        self.assertEqual(
            order3.status,
            'cancelled',
        )