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
        ]
