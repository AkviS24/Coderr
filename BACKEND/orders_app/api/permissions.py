from rest_framework.permissions import BasePermission


class IsOrderBusinessUser(BasePermission):
    """Validate that the user is a business user."""

    def has_permission(self, request, view):
        """Allow access only to business users."""

        return request.user.type == 'business'

    def has_object_permission(self, request, view, obj):
        """Allow access only when the user owns the order."""

        return obj.business_user == request.user


class IsCustomerUser(BasePermission):
    """Validates that the user is a customer."""

    def has_permission(self, request, view):
        """Allow access only to customer users."""

        return request.user.type == 'customer'


class IsStaffUser(BasePermission):
    """Validates that the user is a staff member."""

    def has_permission(self, request, view):
        """Allow access only to staff users."""

        return request.user.is_staff