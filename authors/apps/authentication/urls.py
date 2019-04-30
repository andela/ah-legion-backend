from django.urls import path

from .views import (LoginAPIView, RegistrationAPIView,
                    UserRetrieveUpdateAPIView, SocialAuthenticationView,
                    EmailVerificationView, CreateEmailVerificationTokenAPIView,
                    PasswordResetView)
from ..articles.views import GetAllArticlesForCurrentUser
from authors.apps.articles.views import AllUserArticleReports


app_name = 'authentication'


urlpatterns = [
    path('', UserRetrieveUpdateAPIView.as_view(), name='get users'),
    path('register/', RegistrationAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('oauth/', SocialAuthenticationView.as_view(),
         name='social_login'),
    path('activate/<str:token>',
         EmailVerificationView.as_view(), name='verify email'),
    path('token/', CreateEmailVerificationTokenAPIView.as_view(),
         name='new verification token'),
    path('password-reset/', PasswordResetView.as_view(),
         name='password-reset'),
    path('articles/', GetAllArticlesForCurrentUser.as_view(),
         name='personal-articles'),
    path('article-reports/', AllUserArticleReports.as_view(),
         name='user-article-reports')

]
