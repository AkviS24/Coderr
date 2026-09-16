from django.urls import path

from .views import UserProfileView, BusinessProfilesView, CustomerProfilesView


urlpatterns = [
    path(
        'profile/<int:pk>/',
        UserProfileView.as_view(),
    ),
    path(
        'profiles/business/',
        BusinessProfilesView.as_view(),
    ),
    path(
        'profiles/customer/',
        CustomerProfilesView.as_view(),
    )
]