from django.test import TestCase
from django.db import IntegrityError

from auth_app.models import CustomUser
from ..models import UserProfile


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123!',
        )


    def test_user_to_profile(self):
        profile = UserProfile.objects.create(
            user=self.user,
        )
        self.assertEqual(profile.user, self.user)

    def test_user_only_can_have_1_profile(self):
        UserProfile.objects.create(
            user=self.user,
        )
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(
                user=self.user,
            )

    def test_profile_default_values(self):
        profile = UserProfile.objects.create(
            user=self.user,
        )
        self.assertEqual(profile.location, "")
        self.assertEqual(profile.tel, "")
        self.assertEqual(profile.description, "")
        self.assertEqual(profile.working_hours, "")

    def test_profile_created_at_is_set(self):
        profile = UserProfile.objects.create(
            user=self.user,
        )
        self.assertIsNotNone(profile.created_at)

    def test_profile_file_is_optional(self):
        profile = UserProfile.objects.create(
            user=self.user,
        )
        self.assertFalse(profile.file)

    def test_profile_is_deleted_with_user(self):
        profile = UserProfile.objects.create(
            user=self.user,
        )
        self.user.delete()
        self.assertFalse(
            UserProfile.objects.filter(id=profile.id).exists()
        )