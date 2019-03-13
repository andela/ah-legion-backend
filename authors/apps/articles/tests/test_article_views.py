import json
from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


class ArticleViewsTestCase(TestCase):
    '''This class implements tests for the article model'''
    def setUp(self):
        self.user1 = {
            "user":{
                "email": "user1@mail.com",
                "username": "user1",
                "password": "user1user1"
            }
        }

        self.user2 = {
            "user":{
                "email": "user2@mail.com",
                "username": "user2",
                "password": "user2user2"
            }
        }

        self.user1_credentials = {
            "user": {
                "email": "user1@mail.com",
                "password": "user1user1"
            }
        }
        self.user2_credentials = {
            "user": {
                "email": "user2@mail.com",
                "password": "user2user2"
            }
        }

        self.sample_input = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
                "draft": "Giving exellence high priority"
            }
        }

        client = APIClient()
        #Register Users
        client.post(reverse('authentication:register'), self.user1, format='json')
        client.post(reverse('authentication:register'), self.user2, format='json')

        #Login Users
        user1_login_data = client.post(reverse('authentication:login'), 
                self.user1_credentials, format='json')
        user2_login_data = client.post(reverse('authentication:login'), 
                self.user2_credentials, format='json')

        #Get tokens for the 2 users
        token_user1 = user1_login_data.data['token']
        token_user2 = user2_login_data.data['token']
        
        #Create login headers for the two users
        self.header_user1 = {
            'HTTP_AUTHORIZATION': f'Bearer {token_user1}'
        }
        self.header_user2 = {
            'HTTP_AUTHORIZATION': f'Bearer {token_user2}'
        }

    def test_create_article_success(self):
        client = APIClient()
        response = client.post(reverse('articles:create_article'),
                self.sample_input,**self.header_user1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_article_invalid_data(self):
        sample_input = {
            "article": {
                "description": "Ever wonder how?"
            }
        }
        client = APIClient()
        response = client.post(reverse('articles:create_article'),
                sample_input,**self.header_user1, format='json')
        self.assertEqual(response.status_code, 
                    status.HTTP_400_BAD_REQUEST)

    def test_get_all_articles_not_found(self):
        client = APIClient()
        response = client.get(reverse('articles:get_article'),
                format='json')
        self.assertEqual(response.status_code, 
                    status.HTTP_404_NOT_FOUND)

    def test_get_all_articles_success(self):
        #Create article with user1
        client = APIClient()
        respo = client.post(reverse('articles:create_article'),
                self.sample_input,**self.header_user1, format='json')
        self.assertEqual(respo.status_code, status.HTTP_201_CREATED)

        #Publish article of user1
        my_url = '/api/articles/{}/edit'.format(respo.data['slug'])
        respo1 = client.patch(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_200_OK)

        #Get all articles
        response = client.get(reverse('articles:get_article'),
                format='json')
        self.assertEqual(response.status_code, 
                    status.HTTP_200_OK)

    def test_get_an_article(self):
        client = APIClient()
        respo = client.post(reverse('articles:create_article'),
                self.sample_input,**self.header_user1, format='json')
        self.assertEqual(respo.status_code, status.HTTP_201_CREATED)

        #Get an article that is not there
        my_url = '/api/articles/{}'.format(respo.data['slug'])
        respo1 = client.get(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_404_NOT_FOUND)

        #Publish article of user1
        my_url = '/api/articles/{}/edit'.format(respo.data['slug'])
        respo2 = client.patch(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo2.status_code, status.HTTP_200_OK)

        #Get an article that is there
        my_url = '/api/articles/{}'.format(respo.data['slug'])
        respo3 = client.get(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo3.status_code, status.HTTP_200_OK)

    
    def test_update_article_does_not_exist(self):
        #Create article with user1
        client = APIClient()
        respo = client.post(reverse('articles:create_article'),
                self.sample_input,**self.header_user1, format='json')
        self.assertEqual(respo.status_code, status.HTTP_201_CREATED)

        #Publish article of user1
        my_url = '/api/articles/{}/edit'.format(respo.data['slug'])
        respo1 = client.patch(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_200_OK)

        #Delete article of user1
        respo1 = client.delete(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_200_OK)

        #Try to update the article
        respo1 = client.put(
            my_url,
            self.sample_input,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_404_NOT_FOUND)



    def test_update_article_successfully(self):
        #Create article with user1
        client = APIClient()
        respo = client.post(reverse('articles:create_article'),
                self.sample_input,**self.header_user1, format='json')
        self.assertEqual(respo.status_code, status.HTTP_201_CREATED)

        #Publish article of user1
        my_url = '/api/articles/{}/edit'.format(respo.data['slug'])
        respo1 = client.patch(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_200_OK)

        update_input = {
            "article": {
                "title": "I am a champion",
                "description": "In God we trust.",
                "body": "One step infron of the other",
                "draft": "Giving exellence high priority",
                "activated": True
            }
        }

        #Try to update the article with wrong user
        respo1 = client.put(
            my_url,
            update_input,
            **self.header_user2,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_401_UNAUTHORIZED)

        #Try to update the article with right user
        respo1 = client.put(
            my_url,
            update_input,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_200_OK)

    def test_publish_article_with_no_draft(self):
        sample_input = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe"
            }
        }
        #Create article with user1
        client = APIClient()
        respo = client.post(reverse('articles:create_article'),
                sample_input,**self.header_user1, format='json')
        self.assertEqual(respo.status_code, status.HTTP_201_CREATED)

        #Publish article of user1
        my_url = '/api/articles/{}/edit'.format(respo.data['slug'])
        respo1 = client.patch(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_400_BAD_REQUEST)

