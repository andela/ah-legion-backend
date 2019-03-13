from django.urls import path

from .views import (
    ProfileRetrieveAPIView, ProfilesListAPIView,
    FollowUnfollowAPIView, FollowerFollowingAPIView)

app_name = 'profiles'

urlpatterns = [
    path('profiles/<username>/',
         ProfileRetrieveAPIView.as_view(), name='single-profile'),
    path('profiles/', ProfilesListAPIView.as_view(), name='profiles'),
    path('profiles/<str:username>/follow/',
         FollowUnfollowAPIView.as_view(), name='follow-unfollow'),
    path('profiles/<str:username>/following/',
         FollowerFollowingAPIView.as_view(), name="following"),
]
