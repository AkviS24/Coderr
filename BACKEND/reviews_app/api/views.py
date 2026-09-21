from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Review
from .permissions import IsCustomer
from .serializers import ReviewSerializer


class ReviewListView(APIView):
    """Handle review list and creation requests."""

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Return permissions based on the request method."""

        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomer()]

        return [IsAuthenticated()]

    def _filter_reviews(self, reviews, request):
        """Filter reviews by business user or reviewer."""

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
        return reviews

    def _order_reviews(self, reviews, request):
        """Apply the requested review ordering."""

        ordering = request.query_params.get('ordering')

        if ordering in ['rating', '-rating', 'updated_at', '-updated_at']:
            return reviews.order_by(ordering)

        return reviews

    def get(self, request):
        """Return filtered and ordered reviews."""

        reviews = Review.objects.all()
        reviews = self._filter_reviews(reviews, request)
        reviews = self._order_reviews(reviews, request)

        serializer = ReviewSerializer(reviews, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Create a review for a business."""

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
    """Handle updates and deletion of individual reviews."""

    permission_classes = [IsAuthenticated]

    def get_owned_review(self, request, pk):
        """Return the review if it belongs to the authenticated user."""

        review = get_object_or_404(
            Review,
            pk=pk,
        )

        if review.reviewer != request.user:
            return None

        return review

    def _update_review(self, review, request):
        """Validate and save the updated review."""

        serializer = ReviewSerializer(
            review,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

    def patch(self, request, pk):
        """Update a review owned by the authenticated user."""

        review = self.get_owned_review(request, pk)

        if review is None:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self._update_review(review, request)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def _delete_review(self, review):
        """Delete the given review."""

        review.delete()

    def delete(self, request, pk):
        """Delete a review owned by the authenticated user."""

        review = self.get_owned_review(request, pk)

        if review is None:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        self._delete_review(review)

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
