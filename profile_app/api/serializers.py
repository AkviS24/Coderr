from rest_framework import serializers

from ..models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serialize user profile data."""

    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    type = serializers.CharField(source='user.type')
    email = serializers.EmailField(source='user.email')

    def _update_user(self, instance, user_data):
        for field, value in user_data.items():
            setattr(instance.user, field, value)

        instance.user.save()

    def _update_profile(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})

        self._update_user(instance, user_data)
        self._update_profile(instance, validated_data)

        return instance

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at',
        ]

        read_only_fields = [
            'user',
            'username',
            'file',
            'type',
            'created_at',
        ]


class ProfileListSerializer(serializers.ModelSerializer):
    """Serialize profile list data."""

    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    type = serializers.CharField(source='user.type')

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
        ]