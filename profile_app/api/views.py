from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import UserProfile
from .serializers import UserProfileSerializer



class UserProfileView(APIView):

    def get(self, request, pk):
        profile = UserProfile.objects.get(pk=pk)

        serializer = UserProfileSerializer(profile)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )