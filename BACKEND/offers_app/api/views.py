from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import filter_offers
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
        offers = filter_offers(request, offers)
        return self._paginate_offers(request, offers)

    def _create_offer_details(self, offer, details):
        """Create the detail records belonging to an offer."""

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
            image=request.data.get('image'),
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