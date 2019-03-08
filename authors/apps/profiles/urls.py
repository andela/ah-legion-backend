from django.urls import path

from .views import ProfileRetrieveAPIView, ProfileListApiView

app_name = 'profiles'

urlpatterns = [
    path('profiles/<username>/', ProfileRetrieveAPIView.as_view()),
    path('profiles/', ProfileListApiView.as_view()),
]
