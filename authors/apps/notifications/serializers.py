from .models import Notification
from rest_framework import serializers


class NotificationSerializer(serializers.ModelSerializer):

    read = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'notification_body',
                  'created_at', 'classification', 'read']

    def get_read(self, instance):
        current_user = self.context.get('current_user', None)
        read = Notification.objects.filter(
            pk=instance.pk, read=current_user.id).exists()
        return read

