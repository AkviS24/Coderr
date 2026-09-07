from django.db.models import Q

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Order
from .serializers import OrderSerializer


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(
            Q(customer_user=request.user)
            | Q(business_user=request.user)
        )

        serializer = OrderSerializer(
            orders,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        if request.user.type != 'customer':
            return Response(
                {
                    'details': 'Only users with type customer can create orders.',
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = OrderSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )