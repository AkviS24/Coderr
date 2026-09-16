from unittest.mock import patch
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from profile_app.models import UserProfile


class CustomerProfilesTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='customeruser',
            password='customerpassword123!',
            email='customer@tester.de',
            type='customer',
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
        )
        self.business = CustomUser.objects.create_user(
            username='businessuser',
            password='businesspassword123!',
            email='businesstest@tester.de',
            type='business',
        )
        self.business_profile = UserProfile.objects.create(
            user=self.business,
        )

    def test_get_customer_profiles(self):
        token = Token.objects.create(
            user=self.user,
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}',
        )
        response = self.client.get(
            '/api/profiles/customer/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(response.data),
            1,
        )
        self.assertEqual(
            response.data[0]['username'],
            'customeruser',
        )

    def test_get_customer_profiles_not_authenticated(self):
        response = self.client.get(
            '/api/profiles/customer/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_get_customer_profiles_internal_server_error(self):
        token = Token.objects.create(
            user=self.user,
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}',
        )
        with patch(
            'profile_app.api.views.UserProfile.objects.filter',
            side_effect=Exception,
        ):
            response = self.client.get(
                '/api/profiles/customer/',
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    def test_get_customer_profiles_returns_required_fields(self):
        token = Token.objects.create(
            user=self.user,
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}',
        )
        response = self.client.get(
            '/api/profiles/customer/',
        )
        profile = response.data[0]

        self.assertNotIn(
            'email',
            profile,
        )

        self.assertNotIn(
            'created_at',
            profile,
        )

    def test_get_customer_profiles_empty_fields(self):
        token = Token.objects.create(
            user=self.user,
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}',
        )
        response = self.client.get(
            '/api/profiles/customer/',
        )
        profile = response.data[0]

        self.assertEqual(
            profile['first_name'],
            '',
        )

        self.assertEqual(
            profile['last_name'],
            '',
        )

        self.assertEqual(
            profile['location'],
            '',
        )
        self.assertEqual(
            profile['tel'],
            '',
        )
        self.assertEqual(
            profile['description'],
            '',
        )
        self.assertEqual(
            profile['working_hours'],
            '',
        )

    def test_get_customer_profiles_returns_only_customer_profiles(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            '/api/profiles/customer/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]['type'],
            'customer',
        )