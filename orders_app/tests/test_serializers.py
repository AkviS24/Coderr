from django.test import TestCase

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail
from orders_app.api.serializers import OrderSerializer



class OrderSerializerTest(TestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            username='customer',
            password='testpassword123!',
            type='customer'
        )
        self.business = CustomUser.objects.create_user(
            username='business',
            password='businesspassword123!',
            type='business',
        )
        self.offer = Offer.objects.create(
            user=self.business,
            title='Logo Design',
            description='Professional logo design',
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Logo Design',
            revisions=2,
            delivery_time_in_days=5,
            price=100.00,
            features=['Logo Design'],
            offer_type='basic',
        )

    def test_offer_detail_id_returns_order_with_validated_data(self):
        data = {
            'offer_detail_id': self.offer_detail.id,
        }

        request = self.client.request()
        request.user = self.customer
        serializer = OrderSerializer(
            data=data,
            context={'request': request},
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        order = serializer.save()

        self.assertEqual(
            order.customer_user,
            self.customer,
        )

        self.assertEqual(
            order.business_user,
            self.business,
        )

        self.assertEqual(
            order.title,
            self.offer_detail.title,
        )

        self.assertEqual(
            order.revisions,
            self.offer_detail.revisions,
        )

        self.assertEqual(
            order.delivery_time_in_days,
            self.offer_detail.delivery_time_in_days,
        )

        self.assertEqual(
            order.price,
            self.offer_detail.price,
        )

        self.assertEqual(
            order.features,
            self.offer_detail.features,
        )

        self.assertEqual(
            order.offer_type,
            self.offer_detail.offer_type,
        )

        self.assertEqual(
            order.status,
            'in_progress',
        )