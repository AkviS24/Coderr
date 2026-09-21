from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from ..models import Review


class ReviewListViewTest(APITestCase):
    """Test review list, creation, update, and deletion endpoints."""

    def setUp(self):
        self._create_customer_users()
        self._create_business_users()
        self._create_reviews()
        self.client.force_authenticate(
            user=self.user,
        )

    def _create_customer_users(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123!',
            type='customer',
        )

        self.second_user = CustomUser.objects.create_user(
            username='seconduser',
            password='seconduserpassword123!',
            type='customer',
        )

    def _create_business_users(self):
        self.business_user = CustomUser.objects.create_user(
            username='businessuser',
            password='businessuserpassword123!',
            type='business',
        )

        self.second_business_user = CustomUser.objects.create_user(
            username='secondbusinessuser',
            password='secondbusinesspassword123!',
            type='business',
        )

    def _create_reviews(self):
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

    def _create_new_business_user(self):
        return CustomUser.objects.create_user(
            username='newbusiness',
            password='newbusinesspassword123!',
            type='business',
        )

    def _create_review_for_business(self, business_user):
        return self.client.post(
            '/api/reviews/',
            {
                'business_user': business_user.id,
                'rating': 4,
                'description': 'It was amazing',
            },
        )

    def _update_review(self):
        return self.client.patch(
            f'/api/reviews/{self.review.id}/',
            {
                'rating': 5,
                'description': 'Updated review',
            },
            format='json',
        )

    def _delete_review(self):
        return self.client.delete(
            f'/api/reviews/{self.review.id}/',
        )

    def test_get_reviews_returns_reviews(self):
        response = self.client.get('/api/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_get_reviews_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/reviews/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_reviews_filters_by_business_user(self):
        response = self.client.get(
            f'/api/reviews/?business_user_id={self.business_user.id}',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_reviews_filters_by_reviewer(self):
        response = self.client.get(
            f'/api/reviews/?reviewer_id={self.user.id}',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_reviews_orders_by_rating(self):
        response = self.client.get('/api/reviews/?ordering=rating')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [review['rating'] for review in response.data],
            [2, 4, 5],
        )

    def test_get_reviews_orders_by_rating_descending(self):
        response = self.client.get('/api/reviews/?ordering=-rating')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [review['rating'] for review in response.data],
            [5, 4, 2],
        )

    def test_get_reviews_orders_by_updated_at(self):
        self.second_review.description = 'Updated review.'
        self.second_review.save()
        response = self.client.get('/api/reviews/?ordering=updated_at')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[-1]['id'], self.second_review.id)

    def test_get_reviews_orders_by_updated_at_descending(self):
        self.second_review.description = 'Updated review.'
        self.second_review.save()
        response = self.client.get('/api/reviews/?ordering=-updated_at')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], self.second_review.id)

    def test_get_reviews_allowed_for_business_user(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get('/api/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_review_creates_review(self):
        new_business_user = self._create_new_business_user()
        response = self._create_review_for_business(new_business_user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 4)
        self.assertEqual(response.data['reviewer'], self.user.id)

    def test_post_review_rejects_duplicate_review(self):
        response = self.client.post(
            '/api/reviews/',
            {
                'business_user': self.business_user.id,
                'rating': 5,
                'description': 'Second review for testing.',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_review_rejects_customer_as_business_user(self):
        response = self._create_review_for_business(self.second_user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_review_rejects_invalid_rating(self):
        response = self.client.post(
            '/api/reviews/',
            {
                'business_user': self.second_business_user.id,
                'rating': 6,
                'description': 'Invalid rating.',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_review_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            '/api/reviews/',
            {
                'business_user': self.business_user.id,
                'rating': 5,
                'description': 'Should not be created.',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_review_requires_customer_profile(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post(
            '/api/reviews/',
            {
                'business_user': self.second_business_user.id,
                'rating': 4,
                'description': 'This should be not created.',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_review_updates_rating_and_description(self):
        response = self._update_review()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.description, 'Updated review')

    def test_patch_review_rejects_invalid_rating(self):
        response = self.client.patch(
            f'/api/reviews/{self.review.id}/',
            {'rating': 6},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_review_rejects_business_user(self):
        response = self.client.patch(
            f'/api/reviews/{self.review.id}/',
            {'business_user': self.business_user.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_review_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(
            f'/api/reviews/{self.review.id}/',
            {'rating': 5},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_review_only_creator_can_update(self):
        self.client.force_authenticate(user=self.second_user)
        response = self.client.patch(
            f'/api/reviews/{self.review.id}/',
            {'rating': 5},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_deletes_review(self):
        response = self._delete_review()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())
        self.assertEqual(response.content, b'')

    def test_delete_review_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(f'/api/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_review_only_creator_can_delete(self):
        self.client.force_authenticate(user=self.second_user)
        response = self.client.delete(f'/api/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_returns_404_for_missing_review(self):
        response = self.client.delete('/api/reviews/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
