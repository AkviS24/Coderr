from rest_framework.permissions import BasePermission


class IsOrderBusinessUser(BasePermission):
    """Validate that the user is a business user."""

    def has_permission(self, request, view):
        return request.user.type == 'business'

    def has_object_permission(self, request, view, obj):
        return obj.business_user == request.user