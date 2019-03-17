import json
from django.urls import reverse
from rest_framework import status

from authors.apps.notifications.models import Notification
from .basetest import BaseTest

class TestNotificationViews(BaseTest):
   

    def test_user_get_all_notifications(self):
        """ test for checking if user canm get all the notifications they own """
        token = self.login_user(self.user_data)
        headers = {'HTTP_AUTHORIZATION':'Bearer '+token}
        response = self.client.get(reverse('notifications:all-user-notifications'), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_can_get_a_specific_notification(self):
        """ test if a user can get a specific notification"""
        token = self.login_user(self.user_data)
        headers = {'HTTP_AUTHORIZATION':'Bearer '+token}
        response = self.client.get(reverse('notifications:specific-user-notification', args=(1,)), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['notifications']['id'],1)
    
    def test_user_cannot_get_non_existent_notification(self):
        """ test if user can get a non-existent notification """
        token = self.login_user(self.user_data)
        headers = {'HTTP_AUTHORIZATION':'Bearer '+token}
        response = self.client.get(reverse('notifications:specific-user-notification', args=(34,)), **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()['notifications']['message'],"nofication not found")

    def test_user_can_mark_read_a_specific_notification(self):
        """ test if a user can mark a specific notification as read """
        token = self.login_user(self.user_data)
        headers = {'HTTP_AUTHORIZATION':'Bearer '+token}
        self.client.put("/api/user/notifications/1/", **headers)
        response = self.client.get("/api/user/notifications/1/", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['notifications']['read'], True)

    def test_user_cannot_mark_read_a_non_existent_notification(self):
        """ test if a user can mark a non existent notification as read """
        token = self.login_user(self.user_data)
        headers = {'HTTP_AUTHORIZATION':'Bearer '+token}
        response = self.client.put("/api/user/notifications/67/", **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()['notifications']['message'],"nofication not found")

    def test_user_cannot_mark_read_a_specific_notification_twice(self):
        """ test if a user can mark a specific notification as read more than once"""
        token = self.login_user(self.user_data)
        headers = {'HTTP_AUTHORIZATION':'Bearer '+token}
        self.client.put("/api/user/notifications/1/", **headers)
        response = self.client.put("/api/user/notifications/1/", **headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['notifications']['message'], "you already marked this as read")

    def test_user_can_mark_all_notifications_as_read(self):
        """ test if a user can mark all his notifications as read """
        token = self.login_user(self.user_data)
        headers = {'HTTP_AUTHORIZATION':'Bearer '+token}
        response = self.client.put("/api/user/notifications/", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_cannot_get_in_app_notifications_after_unsubscribing(self):
        """When users unsubscribe from notifications, they should not be able to receive any"""
        self.user1.profile.app_notifications = False
        self.user1.save()
        self.notification3 = Notification.objects.create(notification_body=self.notification_body1)
        token = self.login_user(self.user_data)
        headers = {'HTTP_AUTHORIZATION':'Bearer '+token}
        response = self.client.get("/api/user/notifications/", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_user_can_get_notification_when_followed_author_publishes_article(self):
    #     """When an author publishes an article, all users who follow the author should get a notification"""
    #     # create a user2 to follow the author
        
    #     user1_token = self.login_user(self.user_data)
    #     user1_headers = {'HTTP_AUTHORIZATION':'Bearer ' + user1_token}

    #     self.assertEqual(self.user1.profile.followers.first(), self.user3.profile)
    #     # now we edit the article so it can be published
    #     self.client.put(reverse(
    #         'articles:update_an_article', args=(self.article.slug,)),
    #         **user1_headers, data=json.dumps(self.dict_article),
    #         content_type='application/json')
    #     self.client.patch(reverse(
    #         'articles:update_an_article', args=(self.article.slug,)),
    #         **user1_headers, data=json.dumps(self.dict_article),
    #         content_type='application/json')

    #     token = self.login_user(self.user2_data)
    #     headers = {'HTTP_AUTHORIZATION':'Bearer ' + token}

    #     # we get the primary key of the new notification and pass it in the url 
    #     pk = Notification.objects.all().last().id
    #     response = self.client.get(
    #         '/api/user/notifications/{}/'.format(pk), **headers
    #         )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(
    #         response.data.get('notification_body'),
    #         "Hello there, testuser, just created a new article titled: 'Introducing Notifications'"
    #         )
    #     self.assertEqual(
    #         response.data.get('classification'),
    #         'article-created'
    #     )
    #     self.assertEqual(Notification.objects.get(pk=pk).pk, pk)

    def test_author_gets_notified_when_an_article_is_liked(self):
        """The author should be notified when a reader likes their article"""
        like_data = {
            'is_like': True
        }
        token = self.login_user(self.user2_data)
        headers = {'HTTP_AUTHORIZATION':'Bearer '+ token}
        self.client.post('/api/articles/{}/like/'.format(self.article.slug),
                                    like_data, **headers, format='json')

        author_token = self.login_user(self.user_data)
        author_headers = {'HTTP_AUTHORIZATION':'Bearer '+ author_token}
        pk = Notification.objects.all().last().id
        response = self.client.get(
            '/api/user/notifications/{}/'.format(pk), **author_headers
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Notification.objects.get(pk=pk).pk, pk)

    def test_author_gets_notified_when_an_article_is_favorited(self):
        """The author should be notified when a reader favorites their article"""

        token = self.login_user(self.user2_data)
        headers = {'HTTP_AUTHORIZATION':'Bearer '+ token}
        self.client.post('/api/articles/{}/favorite/'.format(self.article.slug),
                                    **headers, format='json')

        author_token = self.login_user(self.user_data)
        author_headers = {'HTTP_AUTHORIZATION':'Bearer '+ author_token}
        pk = Notification.objects.all().last().id
        response = self.client.get(
            '/api/user/notifications/{}/'.format(pk), **author_headers
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Notification.objects.get(pk=pk).pk, pk)

