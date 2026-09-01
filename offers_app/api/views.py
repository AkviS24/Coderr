from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


from .serializers import OfferSerializer, OfferDetailSerializer
from ..models import Offer, OfferDetail



class OffersView(APIView):

    def get(self, request):
        offers = Offer.objects.all().order_by('-created_at')

        creator_id = request.query_params.get('creator_id')
        if creator_id:
            offers = offers.filter(user_id=creator_id)

        min_price = request.query_params.get('min_price')
        if min_price:
            offers = offers.filter(offerdetail__price__gte=min_price)

        serializer = OfferSerializer(
            offers,
            many=True,
            context={'request': request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
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