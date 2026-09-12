from datetime import timedelta
from io import BytesIO
from PIL import Image

from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail
from offers_app.api.serializers import OfferUpdateSerializer


class OffersTest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='offeruser',
            password='offertestpassword123!',
            email='offermail@tester.de',
            type='business',
        )

        self.offer = Offer.objects.create(
            user=self.user,
            title='Test Offer',
            description='Test description',
        )

        self.required_fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
        ]

    def test_get_offers(self):
        response = self.client.get(
            '/api/offers/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_get_offers_returns_offer(self):
        response = self.client.get(
            '/api/offers/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data['results'][0]['title'],
            'Test Offer',
        )

    def test_get_offers_returns_required_fields(self):
        response = self.client.get(
            '/api/offers/',
        )
        for field in self.required_fields:
            self.assertIn(
                field,
                response.data['results'][0],
            )

    def test_get_offers_returns_details(self):
        OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Offer',
            revisions=2,
            delivery_time_in_days=5,
            price=99.99,
            features=[
                'Feature 1',
                'Feature 2',
            ],
            offer_type='basic',
        )

        response = self.client.get(
            '/api/offers/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        details = response.data['results'][0]['details']

        self.assertEqual(
            len(details),
            1,
        )

        self.assertIn(
            'id',
            details[0],
        )

        self.assertIn(
            'url',
            details[0],
        )

    def test_get_offers_return_user_details(self):
        response = self.client.get(
            '/api/offers/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            'user_details',
            response.data['results'][0],
        )

        self.assertEqual(
            response.data['results'][0]['user_details']['first_name'],
            '',
        )

        self.assertEqual(
            response.data['results'][0]['user_details']['last_name'],
            '',
        )

        self.assertEqual(
            response.data['results'][0]['user_details']['username'],
            'offeruser',
        )

    def test_get_offers_returns_min_price_and_delivery_time(self):
        OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=2,
            delivery_time_in_days=5,
            price=100.00,
            features=['Logo Design'],
            offer_type='basic',
        )

        OfferDetail.objects.create(
            offer=self.offer,
            title='Standard',
            revisions=5,
            delivery_time_in_days=7,
            price=200.00,
            features=['Logo Design', 'Visitenkarte'],
            offer_type='standard',
        )

        OfferDetail.objects.create(
            offer=self.offer,
            title='Premium',
            revisions=10,
            delivery_time_in_days=10,
            price=500.00,
            features=['Logo Design', 'Visitenkarte', 'Flyer'],
            offer_type='premium',
        )

        response = self.client.get(
            '/api/offers/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data['results'][0]['min_price'],
            100,
        )
        self.assertEqual(
            response.data['results'][0]['min_delivery_time'],
            5,
        )

    def test_get_offer_detail(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            f'/api/offers/{self.offer.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data['title'],
            'Test Offer',
        )

    def test_get_offer_detail_requires_authentication(self):
        response = self.client.get(
            f'/api/offers/{self.offer.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_get_offer_detail_returns_404_for_invalid_id(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            '/api/offers/99999/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_get_offer_detail_returns_required_fields(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            f'/api/offers/{self.offer.id}/',
        )

        required_fields = [
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
        ]

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        for field in required_fields:
            self.assertIn(
                field,
                response.data,
            )

    def test_get_offer_detail_returns_offer_data(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            f'/api/offers/{self.offer.id}/',
        )

        self.assertEqual(
            response.data['id'],
            self.offer.id,
        )

        self.assertEqual(
            response.data['user'],
            self.user.id,
        )

        self.assertEqual(
            response.data['title'],
            'Test Offer',
        )

        self.assertEqual(
            response.data['description'],
            'Test description',
        )

    def test_get_offers_returns_newest_offer_first(self):
        older_offer = Offer.objects.create(
            user=self.user,
            title='Older Offer',
            description='Older description',
        )

        newer_offer = Offer.objects.create(
            user=self.user,
            title='Newer Offer',
            description='Newer description',
        )

        response = self.client.get(
            '/api/offers/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['results'][0]['id'],
            newer_offer.id,
        )

        self.assertEqual(
            response.data['results'][1]['id'],
            older_offer.id,
        )

    def test_get_offers_filter_by_creator_id(self):
        other_user = CustomUser.objects.create_user(
            username='therofferuser',
            password='otheroffertestpassword123!',
            email='otherofferuser@tester.de',
            type='business',
        )

        other_offer = Offer.objects.create(
            user=other_user,
            title='Other Offer',
            description='Other description',
        )

        response = self.client.get(
            f'/api/offers/?creator_id={self.user.id}',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data['results']),
            1,
        )

        self.assertEqual(
            response.data['results'][0]['id'],
            self.offer.id,
        )

    def test_get_offers_filters_by_min_price(self):
        OfferDetail.objects.create(
            offer=self.offer,
            title='Cheap Offer',
            revisions=2,
            delivery_time_in_days=5,
            price=50.00,
            features=['Feature 1'],
            offer_type='basic',
        )

        expensive_offer = Offer.objects.create(
            user=self.user,
            title='Expensive Offer',
            description='Expensive description',
        )

        OfferDetail.objects.create(
            offer=expensive_offer,
            title='Expensive Detail',
            revisions=5,
            delivery_time_in_days=7,
            price=150.00,
            features=['Feature 1'],
            offer_type='basic',
        )

        response = self.client.get(
            '/api/offers/?min_price=100',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data['results']),
            1,
        )
        self.assertEqual(
            response.data['results'][0]['id'],
            expensive_offer.id,
        )

    def test_get_offers_filters_by_max_delivery_time(self):
        OfferDetail.objects.create(
            offer=self.offer,
            title='Standard',
            revisions=5,
            delivery_time_in_days=7,
            price=200.00,
            features=['Logo Design', 'Visitenkarte'],
            offer_type='standard',
        )

        expected_offer_after_filtering = Offer.objects.create(
            user=self.user,
            title='Expected Offer',
            description='Expected description',
        )

        OfferDetail.objects.create(
            offer=expected_offer_after_filtering,
            title='Expected Detail',
            revisions=3,
            delivery_time_in_days=3,
            price=150.00,
            features=['Logo Design'],
            offer_type='standard',
        )

        response = self.client.get(
            '/api/offers/?max_delivery_time=5',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['results'][0]['id'],
            expected_offer_after_filtering.id,
        )

        self.assertNotIn(
            self.offer.id,
            [offer['id'] for offer in response.data['results']],
        )

    def test_get_offers_orders_by_updated_at(self):
        older_offer = Offer.objects.create(
            user=self.user,
            title='Older Offer',
            description='Older description',
        )

        newer_offer = Offer.objects.create(
            user=self.user,
            title='Newer Offer',
            description='Newer description',
        )

        now = timezone.now()

        older_offer.updated_at = now - timedelta(days=1)
        older_offer.save(update_fields=['updated_at'])

        newer_offer.updated_at = now
        newer_offer.save(update_fields=['updated_at'])

        response = self.client.get(
            '/api/offers/?ordering=-updated_at',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['results'][0]['id'],
            newer_offer.id,
        )

    def test_get_offers_orders_by_min_price(self):

        cheap_offer = Offer.objects.create(
            user=self.user,
            title='Cheap Offer',
            description='Cheap description',
        )

        expensive_offer = Offer.objects.create(
            user=self.user,
            title='Expensive Offer',
            description='Expensive description',
        )

        OfferDetail.objects.create(
            offer=cheap_offer,
            title='Cheap Detail',
            revisions=2,
            delivery_time_in_days=5,
            price=50.00,
            features=['Feature 1'],
            offer_type='basic',
        )

        OfferDetail.objects.create(
            offer=expensive_offer,
            title='Expansive Detail',
            revisions=5,
            delivery_time_in_days=7,
            price=150.00,
            features=['Feature 1'],
            offer_type='basic',
        )

        response = self.client.get(
            '/api/offers/?ordering=min_price',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['results'][0]['id'],
            cheap_offer.id
        )

        self.assertEqual(
            response.data['results'][1]['id'],
            expensive_offer.id,
        )

    def test_get_offers_searches_by_title(self):
        matching_offer = Offer.objects.create(
            user=self.user,
            title='Logo Design',
            description='Professional business package',
        )

        Offer.objects.create(
            user=self.user,
            title='Website Development',
            description='Frontend and backend development',
        )

        response = self.client.get(
            '/api/offers/?search=Logo',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data['results']),
            1,
        )

        self.assertEqual(
            response.data['results'][0]['id'],
            matching_offer.id,
        )

    def test_get_offers_searches_by_description(self):
        matching_offer = Offer.objects.create(
            user=self.user,
            title='Website Development',
            description='Professional Logo Design package',
        )

        Offer.objects.create(
            user=self.user,
            title='Mobile App Development',
            description='Professional website package',
        )

        response = self.client.get(
            '/api/offers/?search=Logo',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data['results']),
            1,
        )

        self.assertEqual(
            response.data['results'][0]['id'],
            matching_offer.id,
        )

    def test_get_offers_returns_paginated_response(self):
        response = self.client.get(
            '/api/offers/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            'count',
            response.data,
        )

        self.assertIn(
            'next',
            response.data,
        )

        self.assertIn(
            'previous',
            response.data,
        )

        self.assertIn(
            'results',
            response.data,
        )

    def test_get_offers_respects_page_size(self):
        Offer.objects.create(
            user=self.user,
            title='Second Offer',
            description='Second description',
        )

        Offer.objects.create(
            user=self.user,
            title='Third Offer',
            description='Third description',
        )

        Offer.objects.create(
            user=self.user,
            title='Fourth Offer',
            description='Fourth description',
        )

        response = self.client.get(
            '/api/offers/?page_size=2',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['count'],
            4,
        )
        self.assertEqual(
            len(response.data['results']),
            2,
        )

    def test_create_offer_requires_authentication(self):
        response = self.client.post(
            '/api/offers/',
            {
                'title': 'New Offer',
                'description': 'New offer description',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_create_offer_requires_business_user(self):
        customer_user = CustomUser.objects.create_user(
            username='customeruser',
            password='customerofferpassword123!',
            email='customeroffer@tester.de',
            type='customer',
        )

        self.client.force_authenticate(
            user=customer_user,
        )

        response = self.client.post(

            '/api/offers/',
            {
                'title': 'New Offer',
                'description': 'New offer description.',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_create_offer_succesfully(self):
        self.client.force_authenticate(
            user=self.user,
        )

        data = {
            'title': 'New Offer',
            'description': 'New Offer description.',
            'details': [
                {
                    'title': 'Basic',
                    'revisions': 2,
                    'delivery_time_in_days': 5,
                    'price': 100.00,
                    'features': ['Logo Design'],
                    'offer_type': 'basic',
                },
                {
                    'title': 'Standard',
                    'revisions': 5,
                    'delivery_time_in_days': 7,
                    'price': 200.00,
                    'features': ['Logo Design', 'Visitenkarte'],
                    'offer_type': 'standard', 
                },
                {
                    'title': 'Premium',
                    'revisions': 10,
                    'delivery_time_in_days': 10,
                    'price': 500.00,
                    'features': ['Logo Design', 'Visitenkarte', 'Flyer'],
                    'offer_type': 'premium',
                },
            ],
        }

        response = self.client.post(
            '/api/offers/',
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data['title'],
            'New Offer',
        )

        self.assertEqual(
            len(response.data['details']),
            3,
        )

        for detail in response.data['details']:
            self.assertIn(
                'id',
                detail,
            )

    def test_create_offer_saves_image(self):
        offer_data = {
            'title': 'Test Offer',
            'description': 'Test description',
            'details': [
                {
                    'title': 'Basic',
                    'revisions': 2,
                    'delivery_time_in_days': 5,
                    'price': 150.00,
                    'features': ['Logo Design'],
                    'offer_type': 'basic',
                },
                {
                    'title': 'Standard',
                    'revisions': 5,
                    'delivery_time_in_days': 7,
                    'price': 400.00,
                    'features': ['Logo Design', 'Visitenkarte'],
                    'offer_type': 'standard',
                },
                {
                    'title': 'Premium',
                    'revisions': 12,
                    'delivery_time_in_days': 15,
                    'price': 1500.00,
                    'features': ['Logo Design', 'Visitenkarte', 'Flyer'],
                    'offer_type': 'premium',
                },
            ],
        }

        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            '/api/offers/',
            data=offer_data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        offer = Offer.objects.get(
            id=response.data['id'],
        )

        image_buffer = BytesIO()
        Image.new(
            'RGB',
            (1, 1),
            color='white',
        ).save(
            image_buffer,
            format='JPEG',
        )

        image = SimpleUploadedFile(
            'offer.jpg',
            image_buffer.getvalue(),
            content_type='image/jpeg',
        )

        response = self.client.patch(
            f'/api/offers/{offer.id}/',
            {'image': image},
            format='multipart',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        offer.refresh_from_db()

        self.assertTrue(offer.image)
        self.assertTrue(
            offer.image.name.endswith('.jpg'),
        )

    def test_create_offer_returns_complete_details(self):
        self.client.force_authenticate(
            user=self.user,
        )

        data = {
            'title': 'Complete Detail Offer',
            'description': 'Offer with complete details',
            'details': [
                {
                    'title': 'Basic',
                    'revisions': 2,
                    'delivery_time_in_days': 5,
                    'price': 100.00,
                    'features': ['Logo Design'],
                    'offer_type': 'basic',
                },
                {
                    'title': 'Standard',
                    'revisions': 5,
                    'delivery_time_in_days': 7,
                    'price': 200.00,
                    'features': ['Logo Design', 'Vistienkarte'],
                    'offer_type': 'standard',
                },
                {
                    'title': 'Premium',
                    'revisions': 10,
                    'delivery_time_in_days': 10,
                    'price': 500.00,
                    'features': ['Logo Design', 'Visitenkarte', 'Flyer'],
                    'offer_type': 'premium',
                },
            ],
        }

        response = self.client.post(
            '/api/offers/',
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        required_detail_fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
        ]

        for detail in response.data['details']:
            for field in required_detail_fields:
                self.assertIn(
                    field,
                    detail,
                )

    def test_create_offer_requires_three_details(self):
        self.client.force_authenticate(
            user=self.user,
        )

        data = {
            'title': 'Incomplete Offer',
            'description': 'Offer with incomplete details.',
            'details': [
                {
                    'title': 'Basic',
                    'revisions': 2,
                    'delivery_time_in_days': 7,
                    'price': 100.00,
                    'features': ['Logo Design'],
                    'offer_type': 'basic',
                },
                {
                    'title': 'Standard',
                    'revisions': 5,
                    'delivery_time_in_days': 7,
                    'price': 200.00,
                    'features': ['Logo Design', 'Visitenkarte'],
                    'offer_type': 'standard',
                },
            ],
        }

        response = self.client.post(
            '/api/offers/',
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_offer_rejects_invalid_offer_type(self):
        self.client.force_authenticate(
            user=self.user,
        )

        data = {
            'title': 'Invalid Offer',
            'description': 'Offer with invalid detail type.',
            'details': [
                {
                    'title': 'Basic',
                    'revisions': 2,
                    'delivery_time_in_days': 5,
                    'price': 100.00,
                    'features': ['Logo Design'],
                    'offer_type': 'invalid',
                },
                {
                    'title': 'Standard',
                    'revisions': 5,
                    'delivery_time_in_days': 7,
                    'price': 200.00,
                    'features': ['Logo Design'],
                    'offer_type': 'standard',
                },
                {
                    'title': 'Premium',
                    'revisions': 10,
                    'delivery_time_in_days': 10,
                    'price': 500.00,
                    'features': ['Logo Design'],
                    'offer_type': 'premium',
                },
            ],
        }

        response = self.client.post(
            '/api/offers/',
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_offer_requires_title(self):
        self.client.force_authenticate(
            user=self.user,
        )

        data = {
            'description': 'Offer without a title.',
            'details': [
                {
                    'title': 'Basic',
                    'revisions': 2,
                    'delivery_time_in_days': 5,
                    'price': 100.00,
                    'features': ['Logo Design'],
                    'offer_type': 'basic',
                },
                {
                    'title': 'Standard',
                    'revisions': 5,
                    'delivery_time_in_days': 7,
                    'price': 200.00,
                    'features': ['Logo Design', 'Visitenkarte'],
                    'offer_type': 'standard',
                },
                {
                    'title': 'Premium',
                    'revisions': 10,
                    'delivery_time_in_days': 10,
                    'price': 500.00,
                    'features': ['Logo Design', 'Visitenkarte', 'Flyer'],
                    'offer_type': 'premium',
                },
            ],
        }

        response = self.client.post(
            '/api/offers/',
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_offer_accept_image_as_null(self):
        self.client.force_authenticate(
            user=self.user,
        )

        data = {
            'title': 'Offer with no Image',
            'description': 'Offer description',
            'image': None,
            'details': [
                {
                    'title': 'Basic',
                    'revisions': 2,
                    'delivery_time_in_days': 5,
                    'price': 100.00,
                    'features': ['Logo Design'],
                    'offer_type': 'basic',
                },
                {
                    'title': 'Standard',
                    'revisions': 5,
                    'delivery_time_in_days': 7,
                    'price': 200.00,
                    'features': ['Logo Design', 'Visitenkarte'],
                    'offer_type': 'standard',
                },
                {
                    'title': 'Premium',
                    'revisions': 10,
                    'delivery_time_in_days': 10,
                    'price': 500.00,
                    'features': ['Logo Design', 'Visitenkarte', 'Flyer'],
                    'offer_type': 'premium',
                },
            ],
        }

        response = self.client.post(
            '/api/offers/',
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        offer = Offer.objects.get(title='Offer with no Image')
        self.assertFalse(offer.image.name)


    def test_update_offer_serializer_updates_exsisting_details(self):
        basic =OfferDetail.objects.create(
            offer=self.offer,
            title='Basic',
            revisions=2,
            delivery_time_in_days=5,
            price=100.00,
            features=['Logo Design'],
            offer_type='basic',
        )

        standard = OfferDetail.objects.create(
            offer=self.offer,
            title='Standard',
            revisions=5,
            delivery_time_in_days=7,
            price=200.00,
            features=['Logo Design', 'Visitenkarte'],
            offer_type='standard',
        )

        premium = OfferDetail.objects.create(
            offer=self.offer,
            title='Premium',
            revisions=10,
            delivery_time_in_days=10,
            price=500.00,
            features=['Logo Design', 'Visitenkarte', 'Flyer'],
            offer_type='premium',
        )

        basic_id = basic.id
        standard_id = standard.id
        premium_id = premium.id

        data = {
            'title': 'Updated Offer',
            'details': [
                {
                    'id': basic.id,
                    'title': 'Updated Basic',
                    'price': 150.00,
                    'offer_type': 'basic',
                },
            ],
        }

        serializer = OfferUpdateSerializer(
            self.offer,
            data=data,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.offer.refresh_from_db()
        basic.refresh_from_db()
        standard.refresh_from_db()
        premium.refresh_from_db()

        self.assertEqual(
            self.offer.title,
            'Updated Offer',
        )

        self.assertEqual(
            self.offer.description,
            'Test description',
        )

        self.assertEqual(
            basic.id,
            basic_id,
        )

        self.assertEqual(
            basic.title,
            'Updated Basic',
        )

        self.assertEqual(
            basic.price,
            150.00,
        )

        self.assertEqual(
            standard.id,
            standard_id,
        )

        self.assertEqual(
            standard.title,
            'Standard',
        )

        self.assertEqual(
            standard.price,
            200.00,
        )

        self.assertEqual(
            premium.id,
            premium_id,
        )

        self.assertEqual(
            premium.title,
            'Premium',
        )

        self.assertEqual(
            premium.price,
            500.00,
        )

    def test_patch_offer_requires_authentication(self):
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            {
                'title': 'Updated Offer',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_patch_offer_requires_offer_owner(self):
        other_user = CustomUser.objects.create_user(
            username='otherofferuser',
            password='otherpassword123!',
            email='otheruser@tester.de',
            type='business',
        )

        self.client.force_authenticate(
            user=other_user,
        )

        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            {
                'title': 'Updated Offer',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_patch_offer_not_found_returns_404(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.patch(
            '/api/offers/9999/',
            {
                'title': 'Updated Offer',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_patch_offer_updates_title(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            {
                'title': 'Updated Offer',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.offer.refresh_from_db()

        self.assertEqual(
            self.offer.title,
            'Updated Offer',
        )

        self.assertEqual(
            self.offer.description,
            'Test description',
        )

    def test_patch_offer_returns_full_updated_offer(self):

        details = [
            {
                'title': 'Basic',
                'revisions': 2,
                'delivery_time_in_days': 5,
                'price': 100.00,
                'features': ['Logo Design'],
                'offer_type': 'basic',
            },
            {
                'title': 'Standard',
                'revisions': 5,
                'delivery_time_in_days': 7,
                'price': 200.00,
                'features': ['Logo Sesign', 'Visitenkarte'],
                'offer_type': 'standard',
            },
            {
                'title': 'Premium',
                'revisions': 10,
                'delivery_time_in_days': 10,
                'price': 500.00,
                'features': ['Logo Design', 'Visitenkarte', 'Flyer'],
                'offer_type': 'premium',
            },
        ]

        created_details = [
            OfferDetail.objects.create(
                offer=self.offer,
                **detail,
            )
            for detail in details
        ]

        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            {
                'title': 'Updated Offer',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['id'],
            self.offer.id,
        )

        self.assertEqual(
            response.data['title'],
            'Updated Offer',
        )

        self.assertEqual(
            len(response.data['details']),
            3,
        )

        returned_ids = {
            detail['id']
            for detail in response.data['details']
        }

        expected_ids = {
            detail.id
            for detail in created_details
        }

        self.assertEqual(
            returned_ids,
            expected_ids,
        )

        for detail in response.data['details']:
            self.assertIn(
                'title',
                detail,
            )

            self.assertIn(
                'revisions',
                detail,
            )

            self.assertIn(
                'delivery_time_in_days',
                detail,
            )

            self.assertIn(
                'price',
                detail,
            )

            self.assertIn(
                'features',
                detail,
            )

            self.assertIn(
                'offer_type',
                detail,
            )

    def test_delete_offer_as_owner(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.delete(
            f'/api/offers/{self.offer.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Offer.objects.filter(id=self.offer.id).exists(),
        )

    def test_delete_offer_as_non_owner(self):
        other_user = CustomUser.objects.create_user(
            username='Other User',
            password='otherpassword123!',
            email='otheruser@tester.de',
            type='business',
        )

        self.client.force_authenticate(
            user=other_user,
        )

        response = self.client.delete(
            f'/api/offers/{self.offer.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            Offer.objects.filter(id=self.offer.id).exists(),
        )

    def test_delete_offer_requires_authentication(self):
        response = self.client.delete(
            f'/api/offers/{self.offer.id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertTrue(
            Offer.objects.filter(id=self.offer.id).exists(),
        )

    def test_delete_offer_returns_404_not_found(self):
        self.client.force_authenticate(
            user=self.user,
        )

        fake_offer_id = 9999

        response = self.client.delete(
            f'/api/offers/{fake_offer_id}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )