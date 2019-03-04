from django.test import TestCase
from django.urls import reverse
from django.http import HttpRequest as request

from rest_framework import status
from rest_framework.test import APIClient

from authors.apps.authentication.models import User


class JWTAuthenticationTest(TestCase):
    """Test the JWT Authentication implementation"""
    def setUp(self):
        self.user = User.objects.create(username='user1', email='user1@mail.com', password='password')
        self.user_token = self.user.token
        self.user.save()
        self.client = APIClient()

    def test_if_user_gets_token_when_registering(self):
        user_data = {'user': {'username': 'temp_user', 'email': 'temp_user@mail.com', 'password': 'password'}}
        res = self.client.post(reverse('authentication:register'), user_data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', res.data)

    def test_if_user_passes_valid_token_to_access_secured_endpoint(self):
        """Test if a user can access a secured endpoint after providing a valid token"""
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.user_token}'}
        res = self.client.get(reverse('authentication:get users'), **headers)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_failure_if_user_passes_no_token(self):
        """Test if a user can access a secured endpoint without providing a token"""
        res = self.client.get(reverse('authentication:get users'))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.data['detail'], 'Authentication credentials were not provided.')

    def test_failure_if_user_provides_invalid_token(self):
        """Test if an invalid token can be decoded"""
        fake_token = self.user_token + 'ivalid'
        headers = {'HTTP_AUTHORIZATION': f'Bearer {fake_token}'}
        res = self.client.get(reverse('authentication:get users'), **headers)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.data['detail'], 'Ivalid token provided. Authentication failure.')

    def test_failure_if_user_does_not_exist(self):
        """We register a user to get the token, then delete the user from the database. When a user tries to pass the token to access the endpoint, they should be forbidden from proceeding."""
        test_user = User.objects.create(username='test_user', email='test_user@mail.com', password='password')
        test_token = test_user.token
        test_user.delete()
        client = APIClient()
        headers = {'HTTP_AUTHORIZATION': f'Bearer {test_token}'}
        res = client.get(reverse('authentication:get users'), **headers)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.data['detail'], 'User matching this token was not found.')

    def test_failure_because_user_is_inactive(self):
        """Test if an inactive user can be authenticated"""
        inactive_user = User.objects.create(username='inactive_one', email='inactive@mail.com', password='password')
        inactive_user.is_active = False
        inactive_user.save()
        headers = {'HTTP_AUTHORIZATION': f'Bearer {inactive_user.token}'}
        res = self.client.get(reverse('authentication:get users'), **headers)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.data['detail'], 'Forbidden! This user has been deactivated.')
