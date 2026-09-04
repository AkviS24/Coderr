from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import UserProfile
from .serializers import UserProfileSerializer, ProfileListSerializer



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        profile = get_object_or_404(
            UserProfile,
            pk=pk
        )

        serializer = UserProfileSerializer(profile)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        profile = get_object_or_404(
            UserProfile,
            pk=pk,
        )
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
    permission_classes = [IsAuthenticated]

    profile_type = None

    def get_profiles(self):
        return UserProfile.objects.filter(
            user__type=self.profile_type,
        )

    def server_error_response(self):
        return Response(
            {
                'detail': (
                    'Internal Server error while processing the request.'
                )
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    def get(self, request):
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