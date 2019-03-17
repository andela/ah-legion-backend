from .models import Notification
from django.urls import reverse
from django.core import mail
from django.template.loader import render_to_string
from authors.apps.authentication.models import User
from threading import Thread
import datetime


class NotificationDispatcher:
    """ class for sending in app notifications """

    def send_mail_notifications(self, body, recipients=[]):
        template_name = 'email_notification.html'
        context = {'body': body}
        html_message = render_to_string(template_name, context)
        subject = "You have a notification"
        sender = "admin@authorshaven.com"
        thread = Thread(
            target=mail.send_mail, args=[
                subject, body, sender, recipients, html_message]
        )
        thread.setDaemon(True)
        thread.start()

    def article_published(self, request, instance):
        """ send notification to followers when article is created """
        body = "Hello there, {}, just created a new article titled: '{}'".format(
            request.user.username, instance.title.title()
        )
        notification = Notification.objects.create_notification(
            notification_body=body,
            sender=request.user,
            classification="article-created")
        followers = request.user.profile.followers.all()
        recipients = []
        for follower in followers:
            if follower.app_notifications is True:
                notification.subscribers.add(follower.id)
                notification.save()
            if follower.email_notifications is True:
                follower_email = follower.user.email
                recipients.append(follower_email)
        self.send_mail_notifications(body, recipients=recipients)

    def user_followed(self, request, followed):
        """ send notification to a user in case of a following """

        body = "Hello there {}, you are getting popular. {} just folowed you.".format(
            followed.username, request.user.username
        )
        notification = Notification.objects.create_notification(
            notification_body=body,
            sender=request.user,
            classification="user-followed")
        recipients = []
        if followed.profile.app_notifications is True:
            notification.subscribers.add(followed.pk)
            notification.save()
        if followed.profile.email_notifications is True:
            recipients.append(followed.email)
            self.send_mail_notifications(body, recipients=recipients)

    def article_commented(self, request, instance):
        """ 
        send notification to article owner and 
        users who favorited the article in case 
        of a comment
        """
        body = "Hello there, this artcle titled: '{}', has been commented on. Here is the comment : '{}'".format(
            instance.article.title.title(),
            instance.body
        )
        notification = Notification.objects.create_notification(
            sender=request.user,
            notification_body=body,
            classification="article-commented"
        )
        author = instance.author

        favouriters = instance.article.favorites.all()
        notification.subscribers.add(author.id)
        notification.save()
        recipients = []
        for favouriter in favouriters:
            if favouriter.app_notifications is True:
                notification.subscribers.add(favouriter.id)
                notification.save()
            if favouriter.email_notifications is True:
                recipients.append(favouriter.email)
        self.send_mail_notifications(body, recipients=recipients)

    def article_liked(self, request, instance):
        """ 
        send notification to article owner  in case 
        of a like
        """
        body = "Hello there {}. {} liked your article titled: '{}' ".format(
            instance.article_id.author.user.username,
            request.user.username,
            instance.article_id.title.title()
        )
        notification = Notification.objects.create_notification(
            notification_body=body,
            sender=request.user,
            classification="artice-liked"
        )
        recipients = []
        if instance.article_id.author.app_notifications is True:
            notification.subscribers.add(instance.article_id.author.pk)
            notification.save()
        if instance.article_id.author.email_notifications is True:
            recipients.append(instance.article_id.author.user.email)
            self.send_mail_notifications(body, recipients=recipients)

    def article_favourited(self, request, instance):
        """ 
        send notification to article owner  in case 
        of a favourite
        """
        body = "Hello there {}. {} favourited your article titled: '{}' ".format(
            instance.article_id.author.user.username,
            request.user.username,
            instance.article_id.title.title()
        )
        notification = Notification.objects.create_notification(
            notification_body=body,
            sender=request.user,
            classification="artice-favourited"
        )
        recipients = []
        if instance.article_id.author.app_notifications is True:
            notification.subscribers.add(instance.article_id.author.pk)
            notification.save()
        if instance.article_id.author.email_notifications is True:
            recipients.append(instance.article_id.author.user.email)
            self.send_mail_notifications(body, recipients=recipients)

    def comment_commented(self, request, instance):
        """
        send notification to comment owner author
        in case of a comment of a comment
        """
        article_owner = instance.comment.article.author.user
        parent_comment_owner = instance.comment.author.user
        body = "Hello there. {} commented on this comment '{}' with '{}'".format(
            request.user.username,
            instance.comment.body,
            instance.body
        )
        notification = Notification.objects.create_notification(
            notification_body=body,
            sender=request.user,
            classification="comment-commented"
        )
        to_be_notified = [article_owner, parent_comment_owner]
        recipients = []
        for user in to_be_notified:
            if user.profile.app_notifications is True:
                notification.subscribers.add(user.id)
            if user.profile.email_notifications is True:
                recipients.append(user.email)
        self.send_mail_notifications(body, recipients=recipients)

    def article_rated(self, request, instance):
        pass

    def article_reported(self, request, instance):
        pass


notify = NotificationDispatcher()

