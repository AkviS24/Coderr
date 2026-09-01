from django.urls import path

from . import views

urlpatterns = [
    path(
        '',
        views.OffersView.as_view(),
    ),
]