from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


from .serializers import OfferSerializer, OfferDetailSerializer
from ..models import Offer, OfferDetail



class OffersView(APIView):
    def get(self, request):
        offers = Offer.objects.all()

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
        detail = get_object_or_404(
            OfferDetail,
            pk=pk,
        )

        serializer = OfferDetailSerializer(detail)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )