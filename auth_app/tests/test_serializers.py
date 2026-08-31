from django.test import TestCase

from ..api.serializers import RegistrationSerializer


class RegistrationSerializerTest(TestCase):

    def test_valid_registraton_data(self):
        data = {
            'username': 'testuser',
            'email': 'test@tester.de',
            'password': 'testpassword123!',
            'repeated_password': 'testpassword123!',
            'type': 'customer',
        }

        serializer = RegistrationSerializer(data=data)

        self.assertTrue(serializer.is_valid())


    def test_password_must_match(self):
        data = {
            'username': 'testuser',
            'email': 'test@tester.de',
            'password': 'testpassword123!',
            'repeated_password': 'differenttestpassword123!',
            'type': 'customer',
        }

        serializer = RegistrationSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('repeated_password', serializer.errors)


    def test_invalid_user_type(self):
        data = {
            'username': 'testuser',
            'email': 'test@tester.de',
            'password': 'testpassword123!',
            'repeated_password': 'testpassword123!',
            'type': 'invalid',
        }

        serializer = RegistrationSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('type', serializer.errors)
        