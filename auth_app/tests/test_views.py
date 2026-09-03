from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from auth_app.models import CustomUser



class RegistrationViewTest(TestCase):

     def test_registration_returns_token(self):
          data = {
               'username': 'testuser',
               'email': 'test@tester.de',
               'password': 'testpassword123!',
               'repeated_password': 'testpassword123!',
               'type': 'customer', 
          }

          response = self.client.post(
               '/api/registration/',
               data,
          )

          self.assertEqual(
               response.status_code,
               status.HTTP_201_CREATED,
          )

          self.assertIn(
               'token',
               response.data,
          )

     def test_registration_creates_user(self):
          data = {
               'username': 'newuser',
               'email': 'new@tester.de',
               'password': 'testpassword123!',
               'repeated_password': 'testpassword123!',
               'type': 'business',
          }

          response = self.client.post(
               '/api/registration/',
               data,
          )

          self.assertEqual(
               response.status_code,
               status.HTTP_201_CREATED,
          )

          self.assertTrue(
               CustomUser.objects.filter(
                    username='newuser',
               ).exists()
          )


     def test_registration_returns_complete_response(self):
          data = {
               'username': 'tokenuser',
               'email': 'tokenuser@tester.de',
               'password': 'testpassword123!',
               'repeated_password': 'testpassword123!',
               'type': 'customer',
          }

          response = self.client.post(
               '/api/registration/',
               data,
          )

          user = CustomUser.objects.get(
               username='tokenuser',
          )

          token = Token.objects.get(
               user=user,
          )

          self.assertEqual(
               response.status_code,
               status.HTTP_201_CREATED,
          )

          self.assertEqual(
               response.data['username'],
               user.username,
          )

          self.assertEqual(
               response.data['email'],
               user.email,
          )

          self.assertEqual(
               response.data['user_id'],
               user.id,
          )

          self.assertEqual(
               response.data['token'],
               token.key,
          )

     def test_registration_returns_400_for_invalid_data(self):
          data = {
               'username': 'invalid user',
               'email': 'invalid email',
          }

          response = self.client.post(
               '/api/registration/',
               data,
          )

          self.assertEqual(
               response.status_code,
               status.HTTP_400_BAD_REQUEST,
          )

          self.assertEqual(
               CustomUser.objects.filter(
                    username='invalid user'
               ).count(),
               0,
          )