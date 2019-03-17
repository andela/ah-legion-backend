from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification
from .renderers import NotificationRenderer
from .serializers import NotificationSerializer


class ViewAllUserNotifications(ListAPIView):

    permission_classes = (IsAuthenticated,)
    renderer_classes = (NotificationRenderer,)

    def get(self, request):
        """ get method for getting all user notifications """
        user = request.user
        user_notifications = user.notified.all()

        queryset = {'notifications': user_notifications}

        serializer = NotificationSerializer(
            queryset['notifications'],
            many=True,
            context={'current_user': user})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """ put method for marking all notifications as read """
        user = request.user
        Notification.objects.mark_all_as_read(subscriber=user)
        user_notifications = user.notified.all()

        queryset = {'notifications': user_notifications}

        serializer = NotificationSerializer(
            queryset['notifications'],
            many=True,
            context={'current_user': user})

        return Response(serializer.data, status=status.HTTP_200_OK)


class ViewSpeficUserNotification(RetrieveUpdateAPIView):

    permission_classes = (IsAuthenticated,)
    renderer_classes = (NotificationRenderer,)

    def get(self, request, pk):
        """
        get a specific user notification
        given pk as param
        """
        user = request.user
        try:
            specific_notification = user.notified.get(pk=pk)
        except Notification.DoesNotExist:
            return Response({
                "message": "nofication not found"
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = NotificationSerializer(
            specific_notification, context={'current_user': user})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        mark a specific user notification as read
        given a pk, add user ro read field
        """
        user = request.user
        try:
            specific_notification = user.notified.get(pk=pk)
        except Notification.DoesNotExist:
            return Response({
                "message": "nofication not found"
            }, status=status.HTTP_404_NOT_FOUND)
        if Notification.objects.filter(pk=pk, read=user.id).exists():
            return Response({
                "message": "you already marked this as read"},
                status=status.HTTP_400_BAD_REQUEST)

        specific_notification.read.add(user.pk)
        specific_notification.save()
        message = "you have successfully marked this notification as read"
        return Response({"message": message}, status=status.HTTP_200_OK)
