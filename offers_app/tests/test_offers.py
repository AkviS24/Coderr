from datetime import timedelta

from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail


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

        response = self.client.get(
            '/api/offers/?max_delivery_time=5',
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