from django.http import Http404

from rest_framework import serializers

from ..models import Order
from offers_app.models import OfferDetail


class OfferDetailField(serializers.PrimaryKeyRelatedField):
    """Returns 404 when the requested offer detail does not exist."""

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError:
            if str(data).isdigit():
                raise Http404
            raise


class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = OfferDetailField(
        queryset=OfferDetail.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'offer_detail_id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at',
        ]

    def create(self, validated_data):
        offer_detail = validated_data.pop('offer_detail_id')
        customer = self.context['request'].user
        business = offer_detail.offer.user

        return Order.objects.create(
            customer_user=customer,
            business_user=business,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status='in_progress',
        )



class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'status',
        ]