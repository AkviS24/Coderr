from rest_framework.permissions import BasePermission


class IsBusiness(BasePermission):
    """Allow acces only to authenticated business users."""

    def has_permission(self, request, view):
        return(
            request.user.is_authenticated
            and request.user.type == 'business'
        )



class IsOfferOwner(BasePermission):
    """Allow access only to the owner of the requested offer."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user