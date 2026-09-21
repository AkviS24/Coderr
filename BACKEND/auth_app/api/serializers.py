from rest_framework import serializers


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
