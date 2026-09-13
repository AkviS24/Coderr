from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import CustomUser

from ..models import Order
from .permissions import (
    IsCustomerUser,
    IsOrderBusinessUser,
    IsStaffUser,
)
from .serializers import OrderSerializer, OrderStatusSerializer


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

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

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsAuthenticated(), IsOrderBusinessUser()]
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsStaffUser()]
        return [IsAuthenticated()]

    def patch(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
        )
        self.check_object_permissions(request, order)
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
            type='business',
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