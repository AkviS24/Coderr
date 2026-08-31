from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from auth_app.models import CustomUser
from ..models import UserProfile

class UserProfileViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123!',
        )

        self.profile = UserProfile.objects.create(
            user = self.user,
        )

    def test_get_own_profile(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/api/profile/{self.profile.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )