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