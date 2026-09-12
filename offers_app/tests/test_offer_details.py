from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail


class OfferDetailTest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='offeruser',
            password='offerpassword123!',
            email='offermail@tester.de',
            type='business',
        )
        self.client.force_authenticate(
            user=self.user,
        )
        self.offer = Offer.objects.create(
            user=self.user,
            title='Test Offer',
            description='Test Description',
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Offer',
            revisions=2,
            delivery_time_in_days=5,
            price=99.99,
            features=[
                'Feature 1',
                'Feature 2',
            ],
            offer_type='basic',
        )

    def test_get_offer_detail(self):
        response = self.client.get(
            f'/api/offerdetails/{self.offer_detail.id}/',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_get_offer_detail_requires_authentication(self):
        self.client.force_authenticate(
            user=None,
        )

        response = self.client.get(
            f'/api/offerdetails/{self.offer_detail.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_get_offer_detail_returns_404_for_invalid_id(self):
        response = self.client.get(
            '/api/offerdetails/9999/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_offer_detail_returns_required_fields(self):
        response = self.client.get(
            f'/api/offerdetails/{self.offer_detail.id}/',
        )

        required_fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
        ]

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        for field in required_fields:
            self.assertIn(
                field,
                response.data,
            )

    def test_get_offer_detail_returns_correct_data(self):
        response = self.client.get(
            f'/api/offerdetails/{self.offer_detail.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['id'],
            self.offer_detail.id,
        )

        self.assertEqual(
            response.data['title'],
            'Basic Offer',
        )

        self.assertEqual(
            response.data['revisions'],
            2,
        )

        self.assertEqual(
            response.data['delivery_time_in_days'],
            5,
        )

        self.assertEqual(
            response.data['price'],
            '99.99',
        )

        self.assertEqual(
            response.data['features'],
            ['Feature 1', 'Feature 2'],
        )

        self.assertEqual(
            response.data['offer_type'],
            'basic',
        )