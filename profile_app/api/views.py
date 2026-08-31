from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import UserProfile
from .serializers import UserProfileSerializer



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        profile = get_object_or_404(UserProfile, pk=pk)

        serializer = UserProfileSerializer(profile)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )