from .models import Notification
from django.utils.timesince import timesince
from rest_framework import serializers
from datetime import timedelta


class NotificationSerializer(serializers.ModelSerializer):
    
    
    read = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id','notification_body', 'created_at', 'classification', 'read']


    def get_read(self, instance):
        current_user = self.context.get('current_user', None)
        read = Notification.objects.filter(pk=instance.pk,read=current_user.id).exists()
        return read
        