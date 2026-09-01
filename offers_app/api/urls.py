from django.urls import path

from . import views

urlpatterns = [
    path(
        '',
        views.OffersView.as_view(),
    ),
    path(
        '<int:pk>/',
        views.OfferDetailView.as_view(),
    ),
]