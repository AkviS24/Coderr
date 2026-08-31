from rest_framework import serializers


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    repeated_password = serializers.CharField()
    type = serializers.ChoiceField(
        choices = (
            ('customer', 'Customer'),
            ('business', 'Business'),
        ),
    )

    def validate(self, attrs):
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {
                    'repeated_password': 'Password do not match.'
                }
            )

        return attrs