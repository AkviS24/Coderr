from django.test import TestCase

from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest.mock import patch

from auth_app.models import CustomUser


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123!',
            email='test@tester.de',
            type='customer',
        )

    def test_login_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword123!',
        }
        response = self.client.post(
            '/api/login/',
            data,
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn(
            'token',
            response.data,
        )
        self.assertIn(
            'username',
            response.data,
        )
        self.assertIn(
            'email',
            response.data,
        )
        self.assertIn(
            'user_id',
            response.data,
        )
        self.assertEqual(
            response.data['username'],
            self.user.username,
        )
        self.assertEqual(
            response.data['email'],
            self.user.email,
        )
        self.assertEqual(
            response.data['user_id'],
            self.user.id,
        )
        token = Token.objects.get(
            user=self.user,
        )
        self.assertEqual(
            response.data['token'],
            token.key,
        )

    def test_login_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(
            '/api/login/',
            data,
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_login_internal_server_error(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword123!',
        }

        with patch(
            'auth_app.api.views.authenticate',
            side_effect=Exception,
        ):
            response = self.client.post(
                '/api/login/',
                data,
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )