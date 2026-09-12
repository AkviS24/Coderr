from django.shortcuts import get_object_or_404
from django.db.models import F, Min, Q

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    OfferCreateResponseSerializer,
    OfferSerializer,
    OfferCreateSerializer,
    OfferUpdateSerializer,
    OfferDetailSerializer,
)
from ..models import Offer, OfferDetail


class OffersView(APIView):

    def get(self, request):
        offers = Offer.objects.all()

        ordering = request.query_params.get('ordering')

        if ordering == 'min_price':
            offers = offers.annotate(
                ordering_min_price=Min('offerdetail__price'),
            ).order_by(
                F('ordering_min_price').asc(nulls_last=True),
            )

        elif ordering == '-min_price':
            offers = offers.annotate(
                ordering_min_price=Min('offerdetail__price'),
            ).order_by('-ordering_min_price')
        elif ordering in [
            'updated_at',
            '-updated_at',
        ]:
            offers = offers.order_by(ordering)

        elif ordering is not None:
            return Response(
                {'detail': 'Invalid ordering field.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            offers = offers.order_by('-created_at')

        creator_id = request.query_params.get('creator_id')

        if creator_id:
            offers = offers.filter(
                user_id=creator_id,
            )

        max_delivery_time = request.query_params.get('max_delivery_time')

        if max_delivery_time:
            offers = offers.filter(
                offerdetail__delivery_time_in_days__lte=max_delivery_time,
            )

        min_price = request.query_params.get('min_price')

        if min_price:
            offers = offers.filter(
                offerdetail__price__gte=min_price,
            )

        search = request.query_params.get('search')

        if search:
            offers = offers.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search),
            ).distinct()

        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get(
            'page_size',
            10,
        )

        page = paginator.paginate_queryset(
            offers,
            request,
        )

        serializer = OfferSerializer(
            page,
            many=True,
            context={'request': request},
        )

        return paginator.get_paginated_response(
            serializer.data,
        )


    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication credentials were not provided.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if request.user.type != 'business':
            return Response(
                {'detail': 'Only business User can create offers.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if len(request.data.get('details', [])) != 3:
            return Response(
                {'detail': 'Exactly three offer details are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = OfferCreateSerializer(
            data=request.data,
            context={'request': request},
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        offer = Offer.objects.create(
            user=request.user,
            title=request.data.get('title'),
            description=request.data.get('description'),
        )

        for detail_data in serializer.validated_data.get('details', []):
            OfferDetail.objects.create(
                offer=offer,
                title=detail_data.get('title'),
                revisions=detail_data.get('revisions'),
                delivery_time_in_days=detail_data.get('delivery_time_in_days'),
                price=detail_data.get('price'),
                features=detail_data.get('features'),
                offer_type=detail_data.get('offer_type'),
            )

        return Response(
            OfferCreateResponseSerializer(
                offer,
                context={'request': request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


class OfferDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
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

    def patch(self, request, pk):
        offer = get_object_or_404(
            Offer,
            pk=pk,
        )

        if offer.user != request.user:
            return Response(
                {'detail': 'You are not the owner of this Offer.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = OfferUpdateSerializer(
            offer,
            data=request.data,
            partial=True,
            context={'request': request},
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = OfferCreateResponseSerializer(
            offer,
            context={'request': request},
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        offer = get_object_or_404(
            Offer,
            pk=pk,
        )

        if offer.user != request.user:
            return Response(
                {'detail': 'You are not the owner of this offer.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        offer.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class OfferDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
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