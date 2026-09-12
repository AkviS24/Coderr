from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from offers_app.models import Offer
from reviews_app.models import Review


class BaseInfoTestView(APITestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123!',
            type='customer',
        )

        self.business_user = CustomUser.objects.create_user(
            username='testbusiness',
            password='businesspassword123!',
            type='business',
        )

        self.second_business_user = CustomUser.objects.create_user(
            username='secondbusiness',
            password='businesspassword123!',
            type='business',
        )

        Review.objects.create(
            reviewer=self.customer,
            business_user=self.business_user,
            rating=4,
            description='Good work',
        )

        Review.objects.create(
            reviewer=self.customer,
            business_user=self.second_business_user,
            rating=5,
            description='Excellent work',
        )

        Offer.objects.create(
            user=self.business_user,
            title='test offer',
            description='Test description',
        )

    def test_get_base_info_returns_correct_count(self):
        response = self.client.get(
            '/api/base-info/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['review_count'],
            2,
        )

        self.assertEqual(
            response.data['average_rating'],
            4.5,
        )

        self.assertEqual(
            response.data['business_profile_count'],
            2,
        )

        self.assertEqual(
            response.data['offer_count'],
            1,
        )

    def test_get_base_info_returns_zero_for_no_reviews(self):
        Review.objects.all().delete()

        response = self.client.get(
            '/api/base-info/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['review_count'],
            0,
        )

        self.assertEqual(
            response.data['average_rating'],
            0,
        )

    def test_get_base_info_rounds_average_rating(self):
        Review.objects.all().delete()

        second_customer = CustomUser.objects.create_user(
            username='secondcustomer',
            password='secondcustomerpassword123!',
            type='customer',
        )

        Review.objects.create(
            reviewer=self.customer,
            business_user=self.business_user,
            rating=4,
            description='Good work',
        )

        Review.objects.create(
            reviewer=second_customer,
            business_user=self.business_user,
            rating=5,
            description='Excellent work',
        )

        Review.objects.create(
            reviewer=self.customer,
            business_user=self.second_business_user,
            rating=4,
            description='Another review',
        )

        response = self.client.get(
            '/api/base-info/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['average_rating'],
            4.3,
        )