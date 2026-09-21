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
            type='customer',
        )

        self.profile = UserProfile.objects.create(
            user=self.user,
        )

    def test_get_own_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/profile/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_profile_not_found(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profile/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_profile_not_authenticated(self):
        response = self.client.get(f'/api/profile/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_own_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f'/api/profile/{self.user.id}/',
            {
                'first_name': 'Updated First Name',
                'location': 'Hachenburg, Westerwald',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_foreign_profile_forbidden(self):
        other_user = CustomUser.objects.create_user(
            username='otheruser',
            password='otherpassword123!',
            type='customer',
        )
        UserProfile.objects.create(user=other_user)
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f'/api/profile/{other_user.id}/',
            {'location': 'Hachenburg, Westerwald'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_profile_not_authenticated(self):
        response = self.client.patch(
            f'/api/profile/{self.user.id}/',
            {'location': 'Hachenburg, Westerwald'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_profile_not_found(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            '/api/profile/9999/',
            {'location': 'Hachenburg, Westerwald'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_business_profiles_returns_business_users(self):
        business_user = CustomUser.objects.create_user(
            username='businessuser',
            password='businesspassword123!',
            type='business',
        )
        UserProfile.objects.create(user=business_user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], business_user.id)

    def test_get_customer_profiles_returns_customer_users(self):
        customer_user = CustomUser.objects.create_user(
            username='customeruser',
            password='customerpassword123!',
            type='customer',
        )
        UserProfile.objects.create(user=customer_user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profiles/customer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            {item['user'] for item in response.data},
            {self.user.id, customer_user.id},
        )
