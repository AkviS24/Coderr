from django.urls import path

from .views import (
    BusinessProfilesView,
    CustomerProfilesView,
    UserProfileView,
)


urlpatterns = [
    path(
        'profile/<int:user_id>/',
        UserProfileView.as_view(),
    ),
    path(
        'profiles/business/',
        BusinessProfilesView.as_view(),
    ),
    path(
        'profiles/customer/',
        CustomerProfilesView.as_view(),
    ),
]
