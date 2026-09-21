from rest_framework import serializers

from ..models import CustomUser


class RegistrationSerializer(serializers.Serializer):
    """Validate user registration data."""

    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    repeated_password = serializers.CharField()
    type = serializers.ChoiceField(
        choices=(
            ('customer', 'Customer'),
            ('business', 'Business'),
        ),
    )

    def validate_username(self, value):
        """Reject usernames that are already registered."""

        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'A user with this username already exists.',
            )

        return value

    def validate_email(self, value):
        """Reject email addresses that are already registered."""

        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'A user with this email already exists.',
            )

        return value

    def validate(self, attrs):
        """Validate that both password fields match."""

        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {
                    'repeated_password': 'Passwords do not match.'
                }
            )

        return attrs


class LoginSerializer(serializers.Serializer):
    """Validate user login data."""

    username = serializers.CharField()
    password = serializers.CharField()
