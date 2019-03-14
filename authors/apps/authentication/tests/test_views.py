import json

from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APIClient, force_authenticate

import jwt

from authors.apps.authentication.models import User
from authors.apps.core.utils import TokenHandler


class RegistrationViewTest(TestCase):
    """This class defines tests for the RegistrationView class"""

    def setUp(self):
        self.user1 = {"user":
                      {"email": "user1@mail.com",
                       "username": "user1",
                       "password": "password",
                       "callback_url": "http://www.example.com"}
                      }

    def test_user_can_register(self):
        """Test if a user is able to register"""
        client = APIClient()
        response = client.post(
            reverse('authentication:register'), self.user1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LoginViewTest(TestCase):
    """This class defines tests for the LoginView class"""

    def test_registered_user_can_log_in(self):
        """Test if a registered user can log in"""
        client = APIClient()
        user2 = User.objects.create_user(
            username='user2', email='user2@mail.com', password='password')
        user2.is_verified = True
        user2.save()
        response = client.post(reverse('authentication:login'), {
                               'user': {'email': 'user2@mail.com', 'password': 'password'}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)


class UserRetrieveUpdateAPITest(TestCase):
    """This class defines tests for the UserRetrieveUpdateAPIView"""

    def setUp(self):
        self.verified_user = User.objects.create_user(
            username='user1', email='verified@mail.com', password='password')
        self.verified_user.is_verified = True
        self.verified_user.save()
        self.verified_data = {
            'user': {'email': 'verified@mail.com', 'password': 'password'}}
        self.client = APIClient()

    def test_if_we_can_retrieve_user_list(self):
        """Test if a logged in user can retrieve a user list"""

        login_data = self.client.post(reverse('authentication:login'), {
                                      'user': {"email": "verified@mail.com", "password": "password"}}, format='json')
        token = login_data.data['token']
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        response = self.client.get(
            reverse('authentication:get users'), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_if_we_can_update_user_data(self):
        """Test if we can update the user data"""

        update_info = {"user": {
            "email": "user1@mail.com",
            "bio": "I love to be tested",
            "values": "EPIC"
        }}
        login_data = self.client.post(reverse('authentication:login'), {
                                      'user': {"email": "verified@mail.com", "password": "password"}}, format='json')
        token = login_data.data['token']
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        response = self.client.put(
            reverse('authentication:get users'), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EmailVerificationViewTest(TestCase):
    """Test the email verification view"""

    def test_verification_success_if_user_passes_valid_token(self):
        """Users should be able to verify their account if they pass a valid token"""

        byte_token = jwt.encode({
            'data': 'fake',
            'fake': 'data'
        }, settings.SECRET_KEY, algorithm='HS256')
        str_token = byte_token.decode('utf-8')
        res = self.client.get(
            reverse('authentication:verify email', args=(str_token,)))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['error'], 'invalid token')

    def test_verification_failure_if_nonexistent_user_tries_to_verify_account(self):
        """Only registered users should be able to verify their email accounts"""

        byte_token = jwt.encode({
            'email': 'fake@mail.com',
            'username': 'user'
        }, settings.SECRET_KEY, algorithm='HS256')
        str_token = byte_token.decode('utf-8')
        res = self.client.get(
            reverse('authentication:verify email', args=(str_token,)))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res.data['email'],
                         'No user with this email has been registered')

    def test_verified_users_cannot_verify_their_email_again(self):
        """Users who are verified should not be able to request for verification tokens"""

        registered_user = User.objects.create_user(
            username='user', email='user@mail.com', password='password')
        registered_user.is_verified = True
        registered_user.save()

        data = {
            'username': 'user',
            'email': 'user@mail.com'
        }

        byte_token = jwt.encode({
            'username': data['username'],
            'email': data['email']
        }, settings.SECRET_KEY, algorithm='HS256')
        str_token = byte_token.decode('utf-8')

        client = APIClient()
        res = client.get(
            reverse('authentication:verify email', args=(str_token,)))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['email'],
                         'This email has already been verified')

    def test_users_can_get_verified(self):
        """Unverified users should be able to verify their accounts"""
        user = User.objects.create_user(username='blazer', email='blazer@test.com', password='password')
        user.save()

        data = {'email': 'blazer@test.com',
                'username': 'blazer',
                'callback_url': 'http://www.youtube.com'}

        token = TokenHandler().create_verification_token(data)

        client = APIClient()
        res = client.get(reverse('authentication:verify email', args=(token,)))
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)


class CreateEmailVerificationTokenAPIViewTest(TestCase):
    """Here we test if new verification tokens are created"""

    def setUp(self):

        self.registered_user = User.objects.create_user(
            username='registered', email='reg@mail.com', password='password')
        self.registered_user.save()
        self.data = {
            "email": "reg@mail.com",
            "username": "registered",
            "callback_url": "http://www.example.com"
        }

    def test_email_is_sent_to_user(self):
        """We assert that an email can be sent to the user"""

        client = APIClient()
        res = client.post(
            reverse('authentication:new verification token'), self.data, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            res.data['message'], 'New verification token created. Please proceed to your email reg@mail.com to verify your account.')


