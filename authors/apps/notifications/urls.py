from django.urls import path

from .views import ViewAllUserNotifications, ViewSpeficUserNotification
from ..profiles.views import SwitchNotificationsOnOff

app_name = 'notifications'

urlpatterns = [
    path('', ViewAllUserNotifications.as_view(), name='all-user-notifications'),
    path('<pk>/', ViewSpeficUserNotification.as_view(),
         name='specific-user-notification'),
    path('app/switch-notifications/', SwitchNotificationsOnOff.as_view(),
         name='switch-notifications')
]
