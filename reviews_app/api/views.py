from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Review
from .permissions import IsCustomer
from .serializers import ReviewSerializer


class ReviewListView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomer()]

        return [IsAuthenticated()]

    def get(self, request):
        reviews = Review.objects.all()

        business_user_id = request.query_params.get('business_user_id')
        reviewer_id = request.query_params.get('reviewer_id')

        if business_user_id:
            reviews = reviews.filter(
                business_user_id=business_user_id,
            )

        if reviewer_id:
            reviews = reviews.filter(
                reviewer_id=reviewer_id,
            )

        ordering = request.query_params.get('ordering')

        if ordering in ['rating', 'updated_at']:
            reviews = reviews.order_by(ordering)

        serializer = ReviewSerializer(reviews, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ReviewSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_owned_review(self, request, pk):
        review = get_object_or_404(
            Review,
            pk=pk,
        )

        if review.reviewer != request.user:
            return None

        return review

    def patch(self, request, pk):
        review = self.get_owned_review(request, pk)

        if review is None:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ReviewSerializer(
            review,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        review = self.get_owned_review(request, pk)

        if review is None:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        review.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )