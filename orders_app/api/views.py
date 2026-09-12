from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import CustomUser

from ..models import Order
from .serializers import OrderSerializer, OrderStatusSerializer


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


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
        )
        if order.business_user != request.user:
            return Response(
                {
                    'details': 'Only the business user of the order can update it.',
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = OrderStatusSerializer(
            order,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
        )
        if not request.user.is_staff:
            return Response(
                {
                    'details': 'Only staff users can delete orders',
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        order.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        get_object_or_404(
            CustomUser,
            pk=business_user_id,
            type='business',
        )
        order_count = Order.objects.filter(
            business_user_id=business_user_id,
            status='in_progress',
        ).count()

        return Response(
            {
                'order_count': order_count,
            },
            status=status.HTTP_200_OK,
        )


class CompletedOrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        get_object_or_404(
            CustomUser,
            pk=business_user_id,
        )
        completed_order_count = Order.objects.filter(
            business_user_id=business_user_id,
            status='completed',
        ).count()

        return Response(
            {
                'completed_order_count': completed_order_count,
            },
            status=status.HTTP_200_OK,
        )