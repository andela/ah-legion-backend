from django.urls import path

from .views import (LoginAPIView, RegistrationAPIView,
                    UserRetrieveUpdateAPIView, SocialAuthenticationView,
                    EmailVerificationView, CreateEmailVerificationTokenAPIView,
                    PasswordResetView)

app_name = 'authentication'

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name='get users'),
    path('users/', RegistrationAPIView.as_view(), name='register'),
    path('users/login/', LoginAPIView.as_view(), name='login'),
    path('users/oauth/', SocialAuthenticationView.as_view(),
         name='social_login'),
    path(
        'activate/<str:token>',
        EmailVerificationView.as_view(), name='verify email'),
    path('token/', CreateEmailVerificationTokenAPIView.as_view(),
         name='new verification token'),
    path('users/password-reset/', PasswordResetView.as_view(),
         name='password-reset')


]
