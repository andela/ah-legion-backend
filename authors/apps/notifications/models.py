from django.db import models
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
from authors.apps.core.models import TimeStampModel
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


class NotificationManager(models.Manager):
    """ manager for notification model """

    def create_notification(self, sender=None, notification_body=None, classification=None):
        """create a single notification """

        notification = self.model(
            sender=sender, notification_body=notification_body, classification=classification)
        notification.save()
        return notification

    def mark_all_as_read(self, subscriber=None):
        notifications = subscriber.notified.all()
        for notification in notifications:
            if not Notification.objects.filter(pk=notification.id, read=subscriber.pk).exists():
                notification.read.add(subscriber.pk)
                notification.save()


class Notification(TimeStampModel):

    sender = models.ForeignKey(
        User, blank=False, on_delete=models.CASCADE, null=True)
    notification_body = models.TextField(
        'body', max_length=100, null=False, blank=False)
    subscribers = models.ManyToManyField(User, related_name='notified')
    classification = models.CharField('classification', max_length=49)
    read = models.ManyToManyField(User, related_name='read', blank=True)

    class Meta:
        ordering = ['updated_at', 'created_at']

    def __str__(self):
        return self.notification_body

    objects = NotificationManager()

