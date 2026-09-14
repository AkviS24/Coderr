from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import CustomUser
from .serializers import LoginSerializer, RegistrationSerializer


class RegistrationView(APIView):
    """Handle user registration requests."""

    def _create_user(self, serializer):
        return CustomUser.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            type=serializer.validated_data['type'],
        )

    def _create_registration_response(self, user):
        token = Token.objects.create(
            user=user,
        )

        return Response(
            {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id,
            },
            status=status.HTTP_201_CREATED,
        )

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self._create_user(serializer)

        return self._create_registration_response(user)


class LoginView(APIView):
    """Handle user login requests."""

    def _authenticate_user(self, serializer):
        return authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )

    def _create_login_response(self, user):
        token, _ = Token.objects.get_or_create(
            user=user,
        )

        return Response(
            {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = self._authenticate_user(serializer)
        except Exception:
            return Response(
                {
                    'detail': (
                        'Internal Server error while processing the request.'
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if user is None:
            return Response(
                {'detail': 'Invalid Credentials.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self._create_login_response(user)
