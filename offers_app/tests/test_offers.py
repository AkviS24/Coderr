from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail


class OffersTest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='offeruser',
            password='offertestpassword123!',
            email='offermail@tester.de',
            type='business',
        )

        self.offer = Offer.objects.create(
            user=self.user,
            title='Test Offer',
            description='Test description',
        )

        self.required_fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
        ]

    def test_get_offers(self):
        response = self.client.get(
            '/api/offers/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_get_offers_returns_offer(self):
        response = self.client.get(
            '/api/offers/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data[0]['title'],
            'Test Offer',
        )

    def test_get_offers_returns_required_fields(self):
        response = self.client.get(
            '/api/offers/',
        )
        for field in self.required_fields:
            self.assertIn(
                field,
                response.data[0],
            )

    def test_get_offers_returns_details(self):
        OfferDetail.objects.create(
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
        response = self.client.get(
            '/api/offers/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn(
            'details',
            response.data[0],
        )