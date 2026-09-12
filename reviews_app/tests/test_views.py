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

    def test_get_reviews_allowed_for_business_user(self):
        self.client.force_authenticate(
            user=self.business_user,
        )

        response = self.client.get(
            '/api/reviews/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_post_review_creates_review(self):
        new_business_user = CustomUser.objects.create_user(
            username='newbusiness',
            password='newbusinesspassword123!',
            type='business',
        )

        response = self.client.post(
            '/api/reviews/',
            {
                'business_user': new_business_user.id,
                'rating': 4,
                'description': 'It was amazing',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Review.objects.count(),
            4,
        )

        self.assertEqual(
            response.data['reviewer'],
            self.user.id,
        )

    def test_post_review_refects_duplicate_review(self):
        response = self.client.post(
            '/api/reviews/',
            {
                'business_user': self.business_user.id,
                'rating': 5,
                'description': 'Second review for testing.'
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_post_review_requires_authentication(self):
        self.client.force_authenticate(
            user=None,
        )

        response = self.client.post(
            '/api/reviews/',
            {
                'business_user': self.business_user.id,
                'rating': 5,
                'description': 'Should not be created.',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_post_review_requires_customer_profile(self):
        self.client.force_authenticate(
            user=self.business_user,
        )

        response = self.client.post(
            '/api/reviews/',
            {
                'business_user': self.second_business_user.id,
                'rating': 4,
                'description': 'This should be not created.',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_patch_review_updates_rating_and_description(self):
        response = self.client.patch(
            f'/api/reviews/{self.review.id}/',
            {
                'rating': 6,
                'description': 'Updated review',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.review.refresh_from_db()

        self.assertEqual(
            self.review.rating,
            6,
        )

        self.assertEqual(
            self.review.description,
            'Updated review',
        )

    def test_patch_review_rejects_business_user(self):
        response = self.client.patch(
            f'/api/reviews/{self.review.id}/',
            {
                'business_user': self.business_user.id,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_patch_review_requires_authentication(self):
        self.client.force_authenticate(
            user=None,
        )

        response = self.client.patch(
            f'/api/reviews/{self.review.id}/',
            {
                'rating': 5,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_patch_review_only_creator_can_update(self):
        self.client.force_authenticate(
            user=self.second_user,
        )

        response = self.client.patch(
            f'/api/reviews/{self.review.id}/',
            {
                'rating': 5,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_delete_review_deletes_review(self):
        response = self.client.delete(
            f'/api/reviews/{self.review.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Review.objects.filter(
                id=self.review.id,
            ).exists(),
        )

        self.assertEqual(
            response.content,
            b'',
        )

    def test_delete_review_requires_authentication(self):
        self.client.force_authenticate(
            user=None,
        )

        response = self.client.delete(
            f'/api/reviews/{self.review.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_delete_review_only_creator_can_delete(self):
        self.client.force_authenticate(
            user=self.second_user,
        )

        response = self.client.delete(
            f'/api/reviews/{self.review.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_delete_review_returns_404_for_missing_review(self):
        response = self.client.delete(
            f'/api/reviews/9999/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )