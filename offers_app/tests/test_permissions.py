from types import SimpleNamespace

from django.test import TestCase

from offers_app.api.permissions import IsBusiness, IsOfferOwner


class IsBusinessTests(TestCase):
    """Test the business user permission."""

    def setUp(self):
        """Set up the business permission."""
        self.permission = IsBusiness()

    def test_business_user_has_permission(self):
        """Allow authenticated business users."""
        request = SimpleNamespace(
            user=SimpleNamespace(
                is_authenticated=True,
                type='business',
            ),
        )

        result = self.permission.has_permission(request, None)

        self.assertTrue(result)

    def test_customer_user_has_no_permission(self):
        """Reject authenticated customer users."""
        request = SimpleNamespace(
            user=SimpleNamespace(
                is_authenticated=True,
                type='customer',
            ),
        )

        result = self.permission.has_permission(request, None)

        self.assertFalse(result)

    def test_unauthenticated_user_has_no_permission(self):
        """Reject unauthenticated users."""
        request = SimpleNamespace(
            user=SimpleNamespace(
                is_authenticated=False,
                type='business',
            ),
        )

        result = self.permission.has_permission(request, None)

        self.assertFalse(result)


class IsOfferOwnerTests(TestCase):
    """Test the offer owner permission."""

    def setUp(self):
        """Set up the offer owner permission."""
        self.permission = IsOfferOwner()

    def test_offer_owner_has_permission(self):
        """Allow the owner off an offer."""
        user = SimpleNamespace(id=1)
        offer = SimpleNamespace(user=user)
        request = SimpleNamespace(user=user)

        result = self.permission.has_object_permission(
            request,
            None,
            offer,
        )

        self.assertTrue(result)

    def test_other_user_has_no_permission(self):
        """Reject users who do not own the offer."""
        owner = SimpleNamespace(id=1)
        other_user = SimpleNamespace(id=2)
        offer = SimpleNamespace(user=owner)
        request = SimpleNamespace(user=other_user)

        result = self.permission.has_object_permission(
            request,
            None,
            offer,
        )

        self.assertFalse(result)