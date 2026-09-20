from django.contrib import admin
from django.test import TestCase

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from profile_app.models import UserProfile
from reviews_app.models import Review


class AdminRegistrationTest(TestCase):
    """Test that all project models are registered in the admin."""

    def test_all_models_are_registered(self):
        models = [
            CustomUser,
            UserProfile,
            Offer,
            OfferDetail,
            Order,
            Review,
        ]

        for model in models:
            self.assertIn(model, admin.site._registry)