from django.urls import path

from .views import ProfileRetrieveAPIView, ProfilesListAPIView

app_name = 'profiles'

urlpatterns = [
    path('profiles/<username>/', ProfileRetrieveAPIView.as_view()),
    path('profiles/', ProfilesListAPIView.as_view()),
]
