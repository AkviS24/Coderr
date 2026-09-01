from django.urls import path

from .views import UserProfileView, BusinessProfileView


urlpatterns = [
    path(
        'profile/<int:pk>/',
        UserProfileView.as_view(),
    ),
    path(
        'profiles/business/',
        BusinessProfileView.as_view(),
    ),
]