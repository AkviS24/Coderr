from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers

from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serialize review data for API requests and responses."""

    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    rating = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at',
        ]

    def _validate_update(self, attrs):
        """Validate fields allowed for review updates."""

        allowed_fields = {'rating', 'description'}

        if set(attrs) - allowed_fields:
            raise serializers.ValidationError(
                'Only rating and description can be updated.',
            )

        return attrs

    def _validate_create(self, attrs):
        """Validate review creation for a business user."""

        reviewer = self.context['request'].user
        business_user = attrs['business_user']

        if business_user.type != 'business':
            raise serializers.ValidationError(
                {'business_user': 'User must be a business user.'},
            )

        if Review.objects.filter(
            reviewer=reviewer,
            business_user=business_user,
        ).exists():
            raise serializers.ValidationError(
                'You have already reviewed this business.',
            )

        return attrs

    def validate(self, attrs):
        """Validate review data for creation or update."""

        if self.instance:
            return self._validate_update(attrs)

        return self._validate_create(attrs)

    def create(self, validated_data):
        """Create a review for the authenticated customer."""

        reviewer = self.context['request'].user
        return Review.objects.create(
            reviewer=reviewer,
            **validated_data,
        )
