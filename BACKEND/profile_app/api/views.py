from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import UserProfile
from .serializers import UserProfileSerializer, ProfileListSerializer


class UserProfileView(APIView):
    """Handle requests for individual user profiles."""

    permission_classes = [IsAuthenticated]

    def get_profile(self, user_id):
        """Return the profile for the given user ID."""

        return get_object_or_404(
            UserProfile,
            user_id=user_id,
        )

    def get(self, request, user_id):
        """Return the requested user profile."""

        profile = self.get_profile(user_id)
        serializer = UserProfileSerializer(profile)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, user_id):
        """Update the authenticated user's own profile."""

        profile = self.get_profile(user_id)

        if profile.user != request.user:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class ProfileListView(APIView):
    """Handle requests for filtered profile lists."""

    permission_classes = [IsAuthenticated]

    profile_type = None

    def get_profiles(self):
        """Return profiles matching the configured user type."""

        return UserProfile.objects.filter(
            user__type=self.profile_type,
        )

    def server_error_response(self):
        """Return a generic internal server error response."""

        return Response(
            {
                'detail': (
                    'Internal Server error while processing the request.'
                )
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    def get(self, request):
        """Return profiles matching the configured user type."""

        try:
            profiles = self.get_profiles()
        except Exception:
            return self.server_error_response()

        serializer = ProfileListSerializer(
            profiles,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class BusinessProfilesView(ProfileListView):
    profile_type = 'business'


class CustomerProfilesView(ProfileListView):
    profile_type = 'customer'
