from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Review
from .serializers import ReviewSerializer


class ReviewListView(APIView):
    permission_classes = [IsAuthenticated]

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