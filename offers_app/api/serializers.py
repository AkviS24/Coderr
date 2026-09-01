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
