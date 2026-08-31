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


     def test_registration_creates_token_for_user(self):
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
               response.data['token'],
               token.key,
          )