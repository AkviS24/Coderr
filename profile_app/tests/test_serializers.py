from django.test import TestCase

from auth_app.models import CustomUser
from ..models import UserProfile
from ..api.serializers import UserProfileSerializer



class SerializerTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123!',
            first_name='Anton',
            last_name='Tester',
            email='testmail@tester.de',
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
        )

    def test_serializer_contains_expected_fields(self):
        serializer = UserProfileSerializer(self.profile)
        data = serializer.data
        expected_fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at',
        ]

        for field in expected_fields:
            self.assertIn(field, data)


    def test_serializer_user_data(self):
        serializer = UserProfileSerializer(self.profile)
        data = serializer.data

        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['first_name'], self.user.first_name)
        self.assertEqual(data['last_name'], self.user.last_name)
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['type'], self.user.type)


    def test_serializer_profile_data(self):
        serializer = UserProfileSerializer(self.profile)
        data = serializer.data

        self.assertFalse(data['file'])
        self.assertEqual(data['location'], self.profile.location)
        self.assertEqual(data['tel'], self.profile.tel)
        self.assertEqual(data['description'], self.profile.description)
        self.assertEqual(data['working_hours'], self.profile.working_hours)
        self.assertIsNotNone(data['created_at'])


    def test_serializer_read_only_fields(self):
        serializer = UserProfileSerializer(self.profile)
        data = serializer.data
        expected_read_only_fields = {
            'user',
            'username',
            'file',
            'type',
            'created_at',
        }

        self.assertEqual(
            set(serializer.Meta.read_only_fields),
            expected_read_only_fields,
        )


    def test_serializer_accept_editable_profile_data(self):
        data = {
            'first_name': 'Neuer',
            'last_name': 'Name',
            'location': 'Berlin',
            'tel': '987654321',
            'description': 'Neue Beschreibung',
            'working_hours': '10-18',
            'email': 'new@email.de',
        }
        serializer = UserProfileSerializer(
            instance=self.profile,
            data=data,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())


    def test_serializer_ignores_read_only_fields(self):
        data = {
            'username': 'hacker',
            'file': 'hacker.jpg',
            'type': 'business',
            'created_at': '2020-01-01T00:00:00Z',
        }
        serializer = UserProfileSerializer(
            instance=self.profile,
            data=data,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        for field in data:
            self.assertNotIn(field, serializer.validated_data)
