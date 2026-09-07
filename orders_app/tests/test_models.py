from django.test import TestCase

from auth_app.models import CustomUser
from orders_app.models import Order

class OrderModelTest(TestCase):
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
            order.customer_user,
            self.customer,
        )

        self.assertEqual(
            order.business_user,
            self.business,
        )

    def test_order_status(self):
        order1 = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title='In Progress Test Order',
            revisions=3,
            delivery_time_in_days=7,
            price=100.00,
            features=['Logo Design'],
            offer_type='basic',
            status='in_progress',
        )
        order2 = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title='Completed Test Order',
            revisions=3,
            delivery_time_in_days=7,
            price=100.00,
            features=['Logo Design'],
            offer_type='basic',
            status='completed',
        )
        order3 = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title='Cancelled Test Order',
            revisions=3,
            delivery_time_in_days=7,
            price=100.00,
            features=['Logo Design'],
            offer_type='basic',
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