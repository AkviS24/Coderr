from django.db import IntegrityError
from django.test import TestCase

from auth_app.models import CustomUser
from reviews_app.models import Review


class ReviewModelTest(TestCase):
    """Test Review model behavior."""

    def setUp(self):
        self.reviewer = CustomUser.objects.create_user(
            username='reviewer',
            password='testpassword123!',
            type='customer',
        )
        self.business_user = CustomUser.objects.create_user(
            username='business',
            password='testpassword123!',
            type='business',
        )

    def test_review_str(self):
        review = Review.objects.create(
            reviewer=self.reviewer,
            business_user=self.business_user,
            rating=5,
            description='Great service.',
        )

        self.assertEqual(
            str(review),
            'reviewer - business (5/5)',
        )

    def test_review_rejects_duplicate_reviewer_and_business_user(self):
        Review.objects.create(
            reviewer=self.reviewer,
            business_user=self.business_user,
            rating=5,
            description='First review.',
        )

        with self.assertRaises(IntegrityError):
            Review.objects.create(
                reviewer=self.reviewer,
                business_user=self.business_user,
                rating=4,
                description='Second review.',
            )