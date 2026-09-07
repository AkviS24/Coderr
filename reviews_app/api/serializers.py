from rest_framework import serializers

from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)

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

    def validate(self, attrs):
        if self.instance:
            return attrs
        
        reviewer = self.context['request'].user
        business_user = attrs['business_user']

        if Review.objects.filter(
            reviewer=reviewer,
            business_user=business_user,
        ).exists():
            raise serializers.ValidationError(
                'You have already reviewed this business.'
            )

        return attrs

    def create(self, validated_data):
        reviewer = self.context['request'].user
        return Review.objects.create(
            reviewer=reviewer,
            **validated_data,
        )