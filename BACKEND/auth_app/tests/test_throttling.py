from django.core.cache import cache
from django.test import TestCase
from rest_framework import status

from auth_app.models import CustomUser


class AuthenticationThrottleTest(TestCase):
    """Test rate limits for authentication endpoints."""

    def setUp(self):
        cache.clear()

    def test_login_throttles_after_ten_requests_per_minute(self):
        """Reject the eleventh login request within one minute."""

        CustomUser.objects.create_user(
            username='throttleuser',
            password='testpassword123!',
            email='throttleuser@tester.de',
            type='customer',
        )

        data = {
            'username': 'throttleuser',
            'password': 'testpassword123!',
        }

        for _ in range(10):
            response = self.client.post('/api/login/', data)

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
            )

        response = self.client.post('/api/login/', data)

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )
        self.assertIn('Retry-After', response.headers)

    def test_registration_throttles_after_five_requests_per_minute(self):
        """Reject the sixth registration request within one minute."""

        for index in range(5):
            data = {
                'username': f'throttleuser{index}',
                'email': f'throttleuser{index}@tester.de',
                'password': 'testpassword123!',
                'repeated_password': 'testpassword123!',
                'type': 'customer',
            }
            response = self.client.post('/api/registration/', data)

            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
            )

        data = {
            'username': 'throttleuser5',
            'email': 'throttleuser5@tester.de',
            'password': 'testpassword123!',
            'repeated_password': 'testpassword123!',
            'type': 'customer',
        }
        response = self.client.post('/api/registration/', data)

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )
        self.assertIn('Retry-After', response.headers)
