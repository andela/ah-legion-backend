import os
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from unittest import skip

class Test_Social_Authentication(APITestCase):
    """Tests social authentication"""
    url = reverse('authentication:social_login')

    def setUp(self):
        self.provider = "twitter"
        self.data = {
            "access_token": os.environ['TWITTER_ACCESS_TOKEN'],
            "access_token_secret": os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
            "provider": self.provider
        }

    def test_user_successful_social_login(self):
        """Test for successful user login"""
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_provider_message(self):
        self.data = {
            "access_token": os.environ['TWITTER_ACCESS_TOKEN'],
            "access_token_secret": os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
            "provider": "twitt"
        }
        error_msg = """Provider not supported, Please use 'google-oauth2',
             'facebook', or 'twitter'."""
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.data['error'], error_msg)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_credentials(self):
        """Test wrong credentials"""
        self.data = {
            "access_token": os.environ['TWITTER_ACCESS_TOKEN_INVALID'],
            "access_token_secret": os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
            "provider": "twitter"
        }
        error_msg = 'Authentication process canceled'
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.data['error'], error_msg)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @skip("Fails because of expired access keys")
    def test_facebook_oauth(self):
        """Test facebook Oauth"""
        self.data = {
            "access_token": os.environ['FACEBOOK_ACCESS_TOKEN'],
            "access_token_secret": os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
            "provider": "facebook"
        }
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @skip("Fails because of expired access keys")
    def test_google_auth(self):
        """Test Google Oauth"""
        self.data = {
            "access_token": os.environ['GOOGLE_ACCESS_TOKEN'],
            "access_token_secret": os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
            "provider": "google-oauth2"
        }

        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

