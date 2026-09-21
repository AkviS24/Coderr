from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    """Allow access only to authenticated customer users."""

    def has_permission(self, request, view):
        """Allow access only to authenticated customer users."""

        return (
            request.user.is_authenticated
            and request.user.type == 'customer'
        )