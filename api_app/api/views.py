from django.db.models import Avg

from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import CustomUser
from offers_app.models import Offer
from reviews_app.models import Review



class BaseInfoView(APIView):
    def get(self, request):
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(
            average=Avg('rating'),
        )['average'] or 0
        business_profile_count = CustomUser.objects.filter(
            type='business',
        ).count()
        offer_count = Offer.objects.count()

        return Response({
            'review_count': review_count,
            'average_rating': round(average_rating, 1),
            'business_profile_count': business_profile_count,
            'offer_count': offer_count,
        })