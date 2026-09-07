from rest_framework import status
from rest_framework.test import APITestCase

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

        self.staff = CustomUser.objects.create_user(
            username='staffuser',
            password='staffpassword123!',
            type='business',
            is_staff=True,
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

    def test_post_offer_detail_id_to_create_new_order(self):
        self.client.force_authenticate(
            user=self.customer,
        )

        response = self.client.post(
            '/api/orders/',
            {
                'offer_detail_id': self.offer_detail.id,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Order.objects.count(),
            3,
        )

        self.assertEqual(
            response.data['customer_user'],
            self.customer.id,
        )

        self.assertEqual(
            response.data['business_user'],
            self.business.id,
        )

        self.assertEqual(
            response.data['title'],
            self.offer_detail.title,
        )

        self.assertEqual(
            response.data['status'],
            'in_progress',
        )

    def test_post_offer_detail_id_when_not_authenticated(self):
        response = self.client.post(
            '/api/orders/',
            {
                'offer_detail_id': self.offer_detail.id,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_post_offer_detail_id_as_a_business_user(self):
        self.client.force_authenticate(
            user=self.business,
        )

        response = self.client.post(
            '/api/orders/',
            {
                'offer_detail_id': self.offer_detail.id,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_patch_status_to_completed_as_business_user(self):
        self.client.force_authenticate(
            user=self.business,
        )

        response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            {
                'status': 'completed',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            'completed',
        )

    def test_patch_status_as_customer_returns_403(self):
        self.client.force_authenticate(
            user=self.customer,
        )

        response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            {
                'status': 'completed',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_patch_with_invalid_or_missing_status_returns_400(self):
        self.client.force_authenticate(
            user=self.business,
        )

        invalid_response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            {
                'status': 'invalid status',
            },
            format='json',
        )

        missing_response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            {},
            format='json',
        )

        self.assertEqual(
            invalid_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            missing_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_patch_status_not_authenticated_return_401(self):
        response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            {
                'status': 'cancelled',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_patch_unknown_order_id_returns_404(self):
        self.client.force_authenticate(
            user=self.business,
        )

        response = self.client.patch(
            f'/api/orders/99999/',
            {
                'status': 'completed',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_patch_status_only_for_own_orders(self):
        other_business_user = CustomUser.objects.create_user(
            username='other user',
            password='otherpassword123!',
            type='business',
        )

        self.client.force_authenticate(
            user=other_business_user,
        )

        response = self.client.patch(
            f'/api/orders/{self.order.id}/',
            {
                'status': 'completed',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_delete_order_as_a_staff_return_204(self):
        self.client.force_authenticate(
            user=self.staff,
        )

        response = self.client.delete(
            f'/api/orders/{self.order.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Order.objects.filter(
                id=self.order.id,
            ).exists(),
        )

    def test_delete_order_as_a_customer_returns_403(self):
        self.client.force_authenticate(
            user=self.customer,
        )

        response = self.client.delete(
            f'/api/orders/{self.order.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_delete_order_not_authenticated_returns_401(self):
        response = self.client.delete(
            f'/api/orders/{self.order.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_delete_order_with_unknown_id_returns_404(self):
        self.client.force_authenticate(
            user=self.staff,
        )

        response = self.client.delete(
            f'/api/orders/9999/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_delete_order_requires_is_staff_true_or_returns_403(self):
        self.client.force_authenticate(
            user=self.business,
        )

        response = self.client.delete(
            f'/api/orders/{self.order.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )