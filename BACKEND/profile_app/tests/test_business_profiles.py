from unittest.mock import patch

from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from auth_app.models import CustomUser
from profile_app.models import UserProfile



class BusinessProfilesTest(APITestCase):

    def setUp(self):
        cache.clear()
        self.user = CustomUser.objects.create_user(
            username='businessuser',
            password='businesspassword123!',
            email='businesstest@tester.de',
            type='business',
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
        )
        self.customer = CustomUser.objects.create_user(
            username='customeruser',
            password='customerpassword123!',
            email='customer@tester.de',
            type='customer',
        )
        self.customer_profile = UserProfile.objects.create(
            user=self.customer,
        )

    def tearDown(self):
        cache.clear()
        super().tearDown()

    def test_registered_business_user_appears_in_profiles(self):
        registration_data = {
            'username': 'registeredbusiness',
            'email': 'registeredbusiness@tester.de',
            'password': 'businesspassword123!',
            'repeated_password': 'businesspassword123!',
            'type': 'business',
        }

        registration_response = self.client.post(
            '/api/registration/',
            registration_data,
        )

        self.assertEqual(
            registration_response.status_code,
            status.HTTP_201_CREATED,
        )

        user = CustomUser.objects.get(username='registeredbusiness')
        self.client.force_authenticate(user=user)

        response = self.client.get(
            '/api/profiles/business/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(response.data),
            2,
        )
        self.assertEqual(
            response.data[1]['username'],
            'registeredbusiness',
        )

    def test_get_business_profiles(self):
        token = Token.objects.create(
            user=self.user,
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}',
        )
        response = self.client.get(
            '/api/profiles/business/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data[0]['username'],
            'businessuser',
        )

    def test_get_business_profiles_not_authenticated(self):
        response = self.client.get(
            '/api/profiles/business/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_get_business_profiles_internal_server_error(self):
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
                '/api/profiles/business/',
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    def test_get_business_profiles_empty_fields(self):
        token = Token.objects.create(
            user=self.user,
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}',
        )
        response = self.client.get(
            '/api/profiles/business/',
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

    def test_get_business_profiles_returns_required_fields(self):
        token = Token.objects.create(
            user=self.user,
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}',
        )
        response = self.client.get(
            '/api/profiles/business/',
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

    def test_get_business_profiles_only_returns_business_profiles(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            '/api/profiles/business/',
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
            'business',
        )