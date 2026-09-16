from django.urls import path

from .views import ReviewDetailView, ReviewListView

urlpatterns = [
    path(
        '',
        ReviewListView.as_view(),
        name='review-list',
    ),
    path(
        '<int:pk>/',
        ReviewDetailView.as_view(),
        name='review-detail',
    ),
]