from rest_framework.test import APITestCase
from rest_framework import status

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail
from ..models import Order


class OrderViewTest(APITestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            username='customer',
            password='custompassword123!',
            type='customer',
        )

        self.business = CustomUser.objects.create_user(
            username='business',
            password='businesspassword123!',
            type='business',
        )

        self.other_customer = CustomUser.objects.create_user(
            username='other customer',
            password='otherpasssword123!',
            type='customer',
        )

        self.offer = Offer.objects.create(
            user=self.business,
            title='Logo Design',
            description='Professional Logo design.',
        )

        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Logo Design',
            revisions=3,
            delivery_time_in_days=5,
            price=100.00,
            features=['Logo Design'],
            offer_type='basic',
        )

        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title=self.offer_detail.title,
            revisions=self.offer_detail.revisions,
            delivery_time_in_days=self.offer_detail.delivery_time_in_days,
            price=self.offer_detail.price,
            features=self.offer_detail.features,
            offer_type=self.offer_detail.offer_type,
            status='in_progress',
        )

        self.other_order = Order.objects.create(
            customer_user=self.other_customer,
            business_user=self.business,
            title='Other Order',
            revisions=2,
            delivery_time_in_days=3,
            price=150.00,
            features=['Other Feature'],
            offer_type='standard',
            status='in_progress',
        )

    def test_get_orders_returns_only_own_orders_to_authenticated_user(self):
        self.client.force_authenticate(
            user=self.customer,
        )

        response = self.client.get(
            '/api/orders/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        order_ids = [
            order['id']
            for order in response.data
        ]

        self.assertIn(
            self.order.id,
            order_ids,
        )

        self.assertNotIn(
            self.other_order.id,
            order_ids,
        )

    def test_get_orders_returns_business_users_orders(self):
        self.client.force_authenticate(
            user=self.business,
        )

        response = self.client.get(
            '/api/orders/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        order_ids = [
            order['id']
            for order in response.data
        ]

        self.assertIn(
            self.order.id,
            order_ids,
        )

        self.assertIn(
            self.other_order.id,
            order_ids,
        )

    def test_get_orders_requires_authentication(self):
        response = self.client.get(
            '/api/orders/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_get_orders_returns_required_fields(self):
        self.client.force_authenticate(
            user=self.customer,
        )

        response = self.client.get(
            '/api/orders/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        required_fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at',
        ]

        for order in response.data:
            for field in required_fields:
                self.assertIn(
                    field,
                    order,
                )