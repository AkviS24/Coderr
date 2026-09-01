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
        profile = get_object_or_404(UserProfile, pk=pk)

        serializer = UserProfileSerializer(profile)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class BusinessProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profiles = UserProfile.objects.filter(
                user__type='business',
            )
        except Exception:
            return Response(
                {
                    'detail': (
                        'Internal Server error while processing the request.'
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        serializer = ProfileListSerializer(
            profiles,
            many=True,
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )