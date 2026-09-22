from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail


class OfferPatchRegressionTest(APITestCase):
    """Cover offer PATCH detail updates without nested IDs."""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='patchregression',
            password='patchpassword123!',
            email='patchregression@tester.de',
            type='business',
        )
        self.offer = Offer.objects.create(
            user=self.user,
            title='Patch Offer',
            description='Patch description',
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=2,
            delivery_time_in_days=5,
            price=100.00,
            features=['Logo Design'],
            offer_type='basic',
        )
        self.client.force_authenticate(user=self.user)

    def test_patch_detail_without_id_returns_updated_offer(self):
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            {
                'details': [
                    {
                        'title': 'Updated Basic',
                        'price': 120.00,
                        'offer_type': 'basic',
                    },
                ],
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.detail.refresh_from_db()
        self.assertEqual(
            self.detail.title,
            'Updated Basic',
        )
        self.assertEqual(
            self.detail.price,
            120.00,
        )
        self.assertEqual(
            response.data['details'][0]['id'],
            self.detail.id,
        )

    def test_patch_unknown_offer_type_returns_400(self):
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            {
                'details': [
                    {
                        'title': 'Invalid Basic',
                        'offer_type': 'does_not_exist',
                    },
                ],
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_patch_detail_without_offer_type_returns_400(self):
        """Return 400 when a detail update omits offer_type."""
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            {
                'details': [
                    {
                        'title': 'Test',
                        'revisions': 3,
                        'delivery_time_in_days': 6,
                        'price': 120,
                        'features': ['Test'],
                    },
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
