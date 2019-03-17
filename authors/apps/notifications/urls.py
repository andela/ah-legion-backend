from django.urls import path

from .views import ViewAllUserNotifications, ViewSpeficUserNotification
from ..profiles.views import ToggleAppNotifications, ToggleEmailNotifications

app_name = 'notifications'

urlpatterns = [
    path('', ViewAllUserNotifications.as_view(), name='all-user-notifications'),
    path('<pk>/', ViewSpeficUserNotification.as_view(),
         name='specific-user-notification'),
    path('app/toggle-app-notifications/', ToggleAppNotifications.as_view(),
         name='toggle-app-notifications'),
    path('app/toggle-email-notifications/',
         ToggleEmailNotifications.as_view(), name='toggle-email-notifications')
]
