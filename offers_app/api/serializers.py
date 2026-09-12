from django.db import models

from rest_framework import serializers

from ..models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
        ]


class OfferDetailUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
        ]
        extra_kwargs = {
            'title': {'required': False},
            'revisions': {'required': False},
            'delivery_time_in_days': {'required': False},
            'price': {'required': False},
            'features': {'required': False},
            'offer_type': {'required': True},
        }



class OfferUpdateSerializer(serializers.ModelSerializer):
    details = OfferDetailUpdateSerializer(
        source='offerdetail_set',
        many=True,
        required=False,
    )

    def update(self, instance, validated_data):
        details_data = validated_data.pop('offerdetail_set', [])

        instance = super().update(instance, validated_data)

        for detail_data in details_data:
            detail_id = detail_data.pop('id')
            detail = instance.offerdetail_set.get(
                id=detail_id,
            )

            for field, value in detail_data.items():
                setattr(detail, field, value)

            detail.save()

        return instance

    class Meta:
        model = Offer
        fields = [
            'title',
            'image',
            'description',
            'details',
        ]
        extra_kwargs = {
            'title': {'required': False},
            'image': {'required': False},
            'description': {'required': False},
        }



class OfferDetailReferenceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='offerdetail-detail',
    )

    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'url',
        ]



class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailReferenceSerializer(
        source='offerdetail_set',
        many=True,
        read_only=True,
    )

    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    def get_min_price(self, obj):
        min_price = obj.offerdetail_set.aggregate(
            min_price=models.Min('price'),
        )['min_price']

        return min_price

    def get_min_delivery_time(self, obj):
        return obj.offerdetail_set.aggregate(
            min_delivery_time=models.Min('delivery_time_in_days'),
        )['min_delivery_time']

    def get_user_details(self, obj):
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'username': obj.user.username,
        }

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
            'user_details',
        ]



class OfferCreateResponseSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(
        source='offerdetail_set',
        many=True,
        read_only=True,
    )

    class Meta:
        model = Offer
        fields = [
            'id',
            'title',
            'image',
            'description',
            'details',
        ]



class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            'title',
            'image',
            'description',
            'details',
        ]