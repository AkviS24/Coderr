from django.db.models import F, Min, Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Offer, OfferDetail
from .permissions import IsBusiness, IsOfferOwner
from .serializers import (
    OfferCreateResponseSerializer,
    OfferCreateSerializer,
    OfferDetailSerializer,
    OfferSerializer,
    OfferUpdateSerializer,
)


class OffersListView(APIView):
    """Handle listing and creation of offers."""

    def get_permissions(self):
        """Return permissions based on the request method."""

        if self.request.method == 'POST':
            return [IsAuthenticated(), IsBusiness()]

        return []

    def _order_by_min_price(self, offers, descending=False):
        """Order offers by their lowest detail price."""

        offers = offers.annotate(
            ordering_min_price=Min('offerdetail__price'),
        )

        if descending:
            return offers.order_by('-ordering_min_price')

        return offers.order_by(
            F('ordering_min_price').asc(nulls_last=True),
        )

    def _order_offers(self, request, offers):
        """Apply the requested ordering to the offer queryset."""

        ordering = request.query_params.get('ordering')

        if ordering == 'min_price':
            return self._order_by_min_price(offers)

        if ordering == '-min_price':
            return self._order_by_min_price(
                offers,
                descending=True,
            )

        if ordering in ['updated_at', '-updated_at']:
            return offers.order_by(ordering)

        if ordering is not None:
            raise ValidationError(
                {'detail': 'Invalid ordering field.'},
            )

        return offers.order_by('-created_at')

    def _filter_by_creator(self, request, offers):
        """Filter offers by their creator ID."""

        creator_id = request.query_params.get('creator_id')

        if not creator_id:
            return offers

        try:
            creator_id = int(creator_id)
        except ValueError:
            raise ValidationError(
                {'detail': 'Invalid creator_id.'},
            )

        return offers.filter(user_id=creator_id)

    def _get_max_delivery_time(self, request):
        """Read and validate the maximum delivery parameter."""

        max_delivery_time = request.query_params.get('max_delivery_time')

        if not max_delivery_time:
            return None

        try:
            return int(max_delivery_time)
        except ValueError:
            raise ValidationError(
                {'detail': 'Invalid max_delivery_time.'},
            )

    def _filter_by_delivery_time(self, request, offers):
        """Filter offers by their maximum delivery time."""

        max_delivery_time = self._get_max_delivery_time(request)

        if max_delivery_time is None:
            return offers

        return offers.filter(
            offerdetail__delivery_time_in_days__lte=max_delivery_time,
        )

    def _get_min_price(self, request):
        """Read and validate the minimum price parameter."""

        min_price = request.query_params.get('min_price')

        if not min_price:
            return None

        try:
            return float(min_price)
        except ValueError:
            raise ValidationError(
                {'detail': 'Invalid min_price'},
            )

    def _filter_by_min_price(self, request, offers):
        """Filter offers by their minimum detail price."""

        min_price = self._get_min_price(request)

        if min_price is None:
            return offers

        return offers.filter(
            offerdetail__price__gte=min_price,
        )

    def _filter_by_search(self, request, offers):
        """Filter offers by title or description."""

        search = request.query_params.get('search')

        if not search:
            return offers

        return offers.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search),
        ).distinct()

    def _filter_offers(self, request, offers):
        """Apply ordering and all supported offer filters."""

        offers = self._order_offers(request, offers)
        offers = self._filter_by_creator(request, offers)
        offers = self._filter_by_delivery_time(request, offers)
        offers = self._filter_by_min_price(request, offers)
        offers = self._filter_by_search(request, offers)

        return offers

    def _get_paginator(self, request):
        """Create and configure the offer list paginator."""

        page_size = request.query_params.get(
            'page_size',
            10,
        )

        try:
            page_size = int(page_size)
        except ValueError:
            raise ValidationError(
                {'detail': 'Invalid page_size'},
            )

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        return paginator

    def _paginate_offers(self, request, offers):
        """Serialize and return a paginated offer response."""

        paginator = self._get_paginator(request)
        page = paginator.paginate_queryset(offers, request)

        serializer = OfferSerializer(
            page,
            many=True,
            context={'request': request},
        )

        return paginator.get_paginated_response(serializer.data)

    def get(self, request):
        """Return a filtered and paginated list of offers."""

        offers = Offer.objects.all()
        offers = self._filter_offers(request, offers)
        return self._paginate_offers(request, offers)

    def _create_offer_details(self, offer, details):
        """Create the three detail records belonging to an offer."""

        for detail_data in details:
            OfferDetail.objects.create(
                offer=offer,
                title=detail_data.get('title'),
                revisions=detail_data.get('revisions'),
                delivery_time_in_days=detail_data.get(
                    'delivery_time_in_days',
                ),
                price=detail_data.get('price'),
                features=detail_data.get('features'),
                offer_type=detail_data.get('offer_type'),
            )

    def _validate_detail_count(self, request):
        """Ensure exactly three offer details are submitted."""

        if len(request.data.get('details', [])) != 3:
            return Response(
                {'detail': 'Exactly 3 offer details are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return None

    def _create_offer(self, request):
        """Create the main offer record."""

        return Offer.objects.create(
            user=request.user,
            title=request.data.get('title'),
            description=request.data.get('description'),
        )

    def _create_offer_with_details(self, request, serializer):
        """Create an offer and its validated detail records."""

        offer = self._create_offer(request)

        self._create_offer_details(
            offer,
            serializer.validated_data.get('details', []),
        )

        return offer

    def _validate_offer(self, request):
        """Validate the submitted offer data."""

        serializer = OfferCreateSerializer(
            data=request.data,
            context={'request': request},
        )

        serializer.is_valid(raise_exception=True)

        return serializer

    def _build_offer_response(self, request, offer):
        """Build the successful offer creation response."""

        serializer = OfferCreateResponseSerializer(
            offer,
            context={'request': request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def post(self, request):
        """Create an offer for an authenticated business user."""

        detail_error = self._validate_detail_count(request)

        if detail_error:
            return detail_error

        serializer = self._validate_offer(request)
        offer = self._create_offer_with_details(request, serializer)

        return self._build_offer_response(request, offer)


class OfferDetailView(APIView):
    """Handle retrieving, updating, and deleting a single offer."""

    def get_permissions(self):
        """Return permissions based on the request method."""

        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAuthenticated(), IsOfferOwner()]

        return [IsAuthenticated()]

    def get(self, request, pk):
        """Return a single offer by its ID."""

        offer = get_object_or_404(
            Offer,
            pk=pk,
        )

        serializer = OfferSerializer(
            offer,
            context={'request': request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def _update_offer(self, request, offer):
        """Validate and save changes to an offer."""

        serializer = OfferUpdateSerializer(
            offer,
            data=request.data,
            partial=True,
            context={'request': request},
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return serializer

    def _build_update_response(self, request, offer):
        """Build the successful offer update response."""

        serializer = OfferCreateResponseSerializer(
            offer,
            context={'request': request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        """Update an offer owned by the requesting user."""

        offer = get_object_or_404(
            Offer,
            pk=pk,
        )

        self.check_object_permissions(request, offer)
        self._update_offer(request, offer)

        return self._build_update_response(request, offer)

    def delete(self, request, pk):
        """Delete an offer owned by the requesting user."""

        offer = get_object_or_404(
            Offer,
            pk=pk,
        )

        self.check_object_permissions(request, offer)
        offer.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class OfferDetailsView(APIView):
    """Handle retrieving a single offer detail."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Return a single offer detail by its ID."""

        offer_detail = get_object_or_404(
            OfferDetail,
            pk=pk,
        )

        serializer = OfferDetailSerializer(
            offer_detail,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )