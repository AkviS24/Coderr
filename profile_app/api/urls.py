from django.urls import path

from .views import UserProfileView


urlpatterns = [
    path(
        'profile/<int:pk>/',
        UserProfileView.as_view(),
    ),
]