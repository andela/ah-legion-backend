from django.urls import path

from .views import (
    ProfileRetrieveAPIView, ProfilesListAPIView,
    FollowUnfollowAPIView, FollowerFollowingAPIView,
    GetArticlesByAuthor)

app_name = 'profiles'

urlpatterns = [
    path('<username>/',
         ProfileRetrieveAPIView.as_view(), name='single-profile'),
    path('<str:username>/follow/',
         FollowUnfollowAPIView.as_view(), name='follow-unfollow'),
    path('<str:username>/following/',
         FollowerFollowingAPIView.as_view(), name="following"),
    path('<str:username>/articles/',
         GetArticlesByAuthor.as_view(), name="articles"),
    path('', ProfilesListAPIView.as_view(), name='profiles'),
]
