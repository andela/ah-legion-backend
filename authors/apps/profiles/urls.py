from django.urls import path

from .views import (
    ProfileRetrieveAPIView, ProfilesListAPIView,
    FollowUnfollowAPIView, FollowerFollowingAPIView)

app_name = 'profiles'

urlpatterns = [
    path('<username>/',
         ProfileRetrieveAPIView.as_view(), name='single-profile'),
    path('<str:username>/follow/',
         FollowUnfollowAPIView.as_view(), name='follow-unfollow'),
    path('<str:username>/following/',
         FollowerFollowingAPIView.as_view(), name="following"),
    path('', ProfilesListAPIView.as_view(), name='profiles'),
]
