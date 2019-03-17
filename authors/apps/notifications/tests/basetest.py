import json
from django.test import TestCase, Client
from authors.apps.notifications.models import Notification
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article


class BaseTest(TestCase):
    """ class to test the profile models"""

    def setUp(self):
        """ Setup some code that is used by the unittests"""
        self.notification_body = 'this is a sample notification'
        self.notification_body1 = 'this is the 2nd notification'

        self.user_data = {
            "user": {
            "username":"testuser",
            "password":"testpassword",
            "email":"test@test.com"
        }
        }
        self.user1 = User.objects.create_user(username="testuser",email="test@test.com",password="testpassword")
        self.user3 = User.objects.create_user(username="testuser3",email="test3@test.com",password="testpassword")

        self.user1.is_verified = True
        self.user3.is_verified = True
        self.user3.profile.app_notifications =False
        self.user1.profile.email_notifications =False
        self.user3.save()
        self.user1.save()
        self.article = Article.objects.create(
            author=self.user1.profile,
            title='Introducing Notifications',
            body='What are they?',
            draft="They are so cool"
        )

        # this dict object contains serializable data to be passed in a url
        self.dict_article = {
            'author': self.user1.profile,
            'title': self.article.title,
            'body': self.article.body,
            'draft': self.article.draft
            }
        
        self.user2 = User.objects.create_user(
            username='user2', password='password', email='user2@mail.com'
        )
        self.user2.is_verified = True
        self.user2.save()
        # let user2 follow user1
        self.user2.profile.followings.add(self.user1.profile)
        self.user3.profile.followings.add(self.user1.profile)
        self.user2.save()

        self.user2_data = {
                        "user": {
                            "email": "user2@mail.com",
                            "password": "password"
                        }
                    }

        

        # create a notification for testing
        self.notification = Notification.objects.create(notification_body=self.notification_body)
        self.notification1 = Notification.objects.create(notification_body=self.notification_body1)
        
        
        #add notifications to user1 we just created
        self.notification.subscribers.add(self.user1.pk)
        self.notification1.subscribers.add(self.user1.pk)
        self.notification1.read.add(self.user1.pk)

        self.test_client = Client()

    def login_user(self, user_data):
        """
        Reusable function to login user1
        """
        response = self.test_client.post(
            "/api/user/login/", data=json.dumps(user_data), content_type='application/json')
        token = response.json()['user']['token']

        return token
