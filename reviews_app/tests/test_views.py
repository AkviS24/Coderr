from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from ..models import Review


class ReviewListViewTest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123!',
            type='customer',
        )

        self.business_user = CustomUser.objects.create_user(
            username='businessuser',
            password='businesspassword123!',
            type='business',
        )

        self.second_user = CustomUser.objects.create_user(
            username='seconduser',
            password='secondpassword123!',
            type='customer',
        )

        self.second_business_user = CustomUser.objects.create_user(
            username='secondbusiness',
            password='secondbusiness123!',
            type='business',
        )

        self.review = Review.objects.create(
            reviewer=self.user,
            business_user=self.business_user,
            rating=4,
            description='First review',
        )

        self.second_review = Review.objects.create(
            reviewer=self.second_user,
            business_user=self.business_user,
            rating=2,
            description='Second review',
        )

        self.third_review = Review.objects.create(
            reviewer=self.user,
            business_user=self.second_business_user,
            rating=5,
            description='Third review',
        )

        self.client.force_authenticate(
            user=self.user,
        )

    def test_get_reviews_returns_reviews(self):
        response = self.client.get(
            '/api/reviews/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            3,
        )

    def test_get_reviews_requires_authentication(self):
        self.client.force_authenticate(
            user=None,
        )
        response = self.client.get(
            '/api/reviews/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_get_reviews_filters_by_business_user(self):
        response = self.client.get(
            '/api/reviews/?business_user_id='
            f'{self.business_user.id}',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

    def test_get_reviews_filters_by_reviewer(self):
        response = self.client.get(
            '/api/reviews/?reviewer_id='
            f'{self.user.id}',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

    def test_get_reviews_orders_by_rating(self):
        response = self.client.get(
            '/api/reviews/?ordering=rating',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            [review['rating'] for review in response.data],
            [2, 4, 5],
        )

    def test_get_reviews_orders_by_updated_at(self):
        self.second_review.description = 'Updated review.'
        self.second_review.save()

        response = self.client.get(
            '/api/reviews/?ordering=updated_at',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data[-1]['id'],
            self.second_review.id,
        )