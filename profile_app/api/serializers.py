from rest_framework import serializers

from ..models import UserProfile



class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    type = serializers.CharField(source='user.type')
    email = serializers.EmailField(source='user.email')

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})

        for field, value in user_data.items():
            setattr(instance.user, field, value)

        instance.user.save()

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

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