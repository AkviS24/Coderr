from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .serializers import RegistrationSerializer
from ..models import CustomUser


class RegistrationView(APIView):

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = CustomUser.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            type=serializer.validated_data['type']
        )

        token = Token.objects.create(user=user)

        return Response(
            {
                'token': token.key,
            },
            status=status.HTTP_201_CREATED,
        )
