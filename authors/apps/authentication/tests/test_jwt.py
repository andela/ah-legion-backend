from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from authors.apps.authentication.models import User
from authors.apps.authentication.backends import JWTAuthentication


class JWTAuthenticationTest(TestCase):
    """Test the JWT Authentication implementation"""

    def setUp(self):
        self.user = User.objects.create(
            username='user1', email='user1@mail.com', password='password')
        self.login_data = {'user': {
            'email': 'user2@mail.com',
            'password': 'password'
        }}
        self.user_token = self.user.token
        self.user.save()
        self.client = APIClient()

    def test_user_gets_a_token_when_they_log_in(self):
        """Users should get a token when they successfully log in"""
        client = APIClient()
        user2 = User.objects.create_user(
            username='user2', email='user2@mail.com', password='password')
        user2.is_verified = True
        user2.save()
        response = client.post(reverse('authentication:login'), {
                               'user': {'email': 'user2@mail.com', 'password': 'password'}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_if_user_passes_valid_token_to_access_secured_endpoint(self):
        """Test if a user can access a secured endpoint after providing a valid token"""
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.user_token}'}
        res = self.client.get(reverse('authentication:get users'), **headers)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_failure_if_user_passes_no_token(self):
        """Test if a user can access a secured endpoint without providing a token"""
        res = self.client.get(reverse('authentication:get users'))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            res.data['detail'], 'Authentication credentials were not provided.')

    def test_failure_if_user_provides_invalid_token(self):
        """Test if an invalid token can be decoded"""
        fake_token = self.user_token + 'ivalid'
        headers = {'HTTP_AUTHORIZATION': f'Bearer {fake_token}'}
        res = self.client.get(reverse('authentication:get users'), **headers)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            res.data['detail'], 'Invalid token provided. Authentication failure.')

    def test_failure_if_user_does_not_exist(self):
        """We register a user to get the token, then delete the user from the database.
        When a user tries to pass the token to access the endpoint, they should be forbidden from proceeding."""
        test_user = User.objects.create(
            username='test_user', email='test_user@mail.com', password='password')
        test_token = test_user.token
        test_user.delete()
        client = APIClient()
        headers = {'HTTP_AUTHORIZATION': f'Bearer {test_token}'}
        res = client.get(reverse('authentication:get users'), **headers)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.data['detail'],
                         'User matching this token was not found.')

    def test_failure_because_user_is_inactive(self):
        """Test if an inactive user can be authenticated"""
        inactive_user = User.objects.create(
            username='inactive_one', email='inactive@mail.com', password='password')
        inactive_user.is_active = False
        inactive_user.save()
        headers = {'HTTP_AUTHORIZATION': f'Bearer {inactive_user.token}'}
        res = self.client.get(reverse('authentication:get users'), **headers)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.data['detail'],
                         'Forbidden! This user has been deactivated.')

    def test_authentication_failure_because_header_is_None(self):
        """Test if authentication fails when a request has authorization
        headers with a length of 0"""
        jwt_auth = JWTAuthentication()
        factory = APIRequestFactory()
        request = factory.get(reverse('authentication:get users'))
        request.META['HTTP_AUTHORIZATION'] = ''
        res = jwt_auth.authenticate(request)
        self.assertEqual(res, None)

    def test_authentication_failure_because_header_length_is_1(self):
        """Test if authentication fails when a request has authorization
        headers with a length of 1"""
        jwt_auth = JWTAuthentication()
        factory = APIRequestFactory()
        request = factory.get(reverse('authentication:get users'))
        request.META['HTTP_AUTHORIZATION'] = 'length'
        res = jwt_auth.authenticate(request)
        self.assertEqual(res, None)

    def test_authentication_failure_if_header_length_is_greater_than_2(self):
        """Test if authentication fails when a request has authorization
        headers with a length greater than 2"""
        jwt_auth = JWTAuthentication()
        factory = APIRequestFactory()
        request = factory.get(reverse('authentication:get users'))
        request.META['HTTP_AUTHORIZATION'] = b'length is greater than 2'
        res = jwt_auth.authenticate(request)
        self.assertEqual(res, None)

    def test_authentication_failure_if_prefixes_mismatch(self):
        """We unit test our authentication method to see if the method
        returns `None` when the prefixes mismatch"""
        jwt_auth = JWTAuthentication()
        factory = APIRequestFactory()
        request = factory.get(reverse('authentication:get users'))
        request.META['HTTP_AUTHORIZATION'] = 'Token, {}'.format(self.user_token)
        res = jwt_auth.authenticate(request)
        self.assertEqual(res, None)
