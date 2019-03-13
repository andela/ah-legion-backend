from datetime import datetime, timedelta
import jwt
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.test import APITestCase
from authors.apps.authentication.serializers import PasswordResetTokenSerializer
from authors.apps.core.utils import TokenHandler
from authors.apps.authentication.models import User, PasswordResetToken


class PasswordResetTestCase(APITestCase):
    """Tests for password reset functionality."""
    register_url = reverse('authentication:register')
    url = reverse('authentication:password-reset')

    def test_valid_request(self):
        """Tests for a valid request for a password reset link."""
        signup_data = {
            "user": {
                "username": "Mary",
                "email": "mary@gmail.com",
                "password": "Mary1234",
                "callback_url": "https://medium.com"
            }
        }

        payload = {
            "payload": {
                "email": "mary@gmail.com",
                "callback_url": "https://medium.com"

            }
        }

        valid_request_response = {"message":
                                  "A password reset link has been sent to your "
                                  "email."
}
        self.client.post(self.register_url, signup_data, format='json')
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.data, valid_request_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_registered_email(self):
        """Tests for a request with an unregistered user email."""
        payload = {
            "payload": {
                "email": "maryperry@gmail.com",
                "callback_url": "https://medium.com"

            }
        }

        valid_request_response = {"message":
                                  "A password reset link has been sent to your "
                                  "email."
                                  }

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.data, valid_request_response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_new_password(self):
        """Tests for a request with a valid new password."""
        signup_data = {
            "user": {
                "username": "Mary",
                "email": "mary@gmail.com",
                "password": "Mary1234",
                "callback_url": "https://medium.com"
            }
        }

        payload = {
                "email": "mary@gmail.com",
                "callback_url": "https://medium.com"

            }
        token = TokenHandler().create_verification_token(payload)

        data = {
            "user_password": {
                "password": "mary1234",
                "confirm_password": "mary1234",
                "token": token
            }
        }
        self.client.post(self.register_url, signup_data, format='json')
        user = get_object_or_404(User, email="mary@gmail.com")
        user_id = user.id
        token_data = {
            "user": user_id,
            "token": token
        }
        serializer = PasswordResetTokenSerializer(data=token_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data_response = {"message": "Your password has been changed."}
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.data, data_response)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_invalid_token(self):
        """Tests for a request with an invalid token."""
        signup_data = {
            "user": {
                "username": "Mary",
                "email": "mary@gmail.com",
                "password": "Mary1234",
                "callback_url": "https://medium.com"
            }
        }
        token_expiry = datetime.now() + timedelta(hours=12)
        token = jwt.encode({
            'email': "mary123@gmail.com",
            'callback_url': "https://medium.com",
            'exp': int(token_expiry.strftime('%s'))},
            settings.SECRET_KEY, algorithm='HS256')

        invalid_token = token.decode('utf-8')

        data = {
            "user_password": {
                "password": "mary1234",
                "confirm_password": "mary1234",
                "token": invalid_token
            }
        }

        data_response = {'message': 'A user with the given token does not exist.'}
        self.client.post(self.register_url, signup_data, format='json')
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.data, data_response)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_using_same_link_twice(self):
        """Tests for a request with an already used token."""
        signup_data = {
            "user": {
                "username": "Mary",
                "email": "mary@gmail.com",
                "password": "Mary1234",
                "callback_url": "https://medium.com"
            }
        }
        payload = {
            "email": "mary@gmail.com",
            "callback_url": "https://medium.com"

        }

        token = TokenHandler().create_verification_token(payload)

        data = {
            "user_password": {
                "password": "mary1234",
                "confirm_password": "mary1234",
                "token": token
            }
        }

        data_response = {"message": "Sorry, we couldn't find that password reset key in our database."
                                    " Please send another request."}

        self.client.post(self.register_url, signup_data, format='json')
        user = get_object_or_404(User, email="mary@gmail.com")
        user_id = user.id
        token_data = {
            "user": user_id,
            "token": token
        }
        serializer = PasswordResetTokenSerializer(data=token_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.client.post(self.register_url, signup_data, format='json')
        self.client.put(self.url, data, format='json')
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.data, data_response)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_blank_password(self):
        """Tests for a request with a blank password."""
        signup_data = {
            "user": {
                "username": "Mary Jane",
                "email": "maryjane@gmail.com",
                "password": "Mary1234",
                "callback_url": "https://medium.com"
            }
        }
        payload = {
                "email": "maryjane@gmail.com",
                "callback_url": "https://www.youtube.com/"

            }

        token = TokenHandler().create_verification_token(payload)
        blank_password_data = {
            "user_password": {
                "password": "",
                "confirm_password": "",
                "token": token
            }
        }

        blank_password_data_response = {"errors": {
            "password": ["Password field cannot be blank"]
        }
        }
        self.client.post(self.register_url, signup_data, format='json')
        response = self.client.put(self.url, blank_password_data, format='json')
        self.assertEqual(response.data, blank_password_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_password_field(self):
        """Tests for a request with no password field."""
        signup_data = {
            "user": {
                "username": "Mary Jane",
                "email": "maryjane@gmail.com",
                "password": "Mary1234",
                "callback_url": "https://medium.com"
            }
        }
        payload = {
            "email": "maryjane@gmail.com",
            "callback_url": "https://www.youtube.com/"

        }
        token = TokenHandler().create_verification_token(payload)
        blank_password_data = {
            "user_password": {
                "password": "",
                "confirm_password": "",
                "token": token
            }
        }

        blank_password_data_response = {"errors": {
            "password": ["Password field cannot be blank"]
        }
        }
        self.client.post(self.register_url, signup_data, format='json')
        response = self.client.put(self.url, blank_password_data, format='json')
        self.assertEqual(response.data, blank_password_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_alphanumeric_password(self):
        """"Tests for a request with a password that is not alphanumeric."""
        signup_data = {
            "user": {
                "username": "Mary Jane",
                "email": "maryjane@gmail.com",
                "password": "Mary1234",
                "callback_url": "https://medium.com"
            }
        }
        payload = {
            "email": "maryjane@gmail.com",
            "callback_url": "https://www.youtube.com/"

        }
        token = TokenHandler().create_verification_token(payload)
        not_alphanumeric_password_data = {
            "user_password": {
                "password": "@343212#@!",
                "confirm_password": "@343212#@!",
                "token": token
            }
        }

        not_alphanumeric_password_data_response = {"errors": {
            "password": ["Password should be alphanumeric"]
        }
        }
        self.client.post(self.register_url, signup_data, format='json')
        response = self.client.put(self.url, not_alphanumeric_password_data, format='json')
        self.assertEqual(response.data, not_alphanumeric_password_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_password(self):
        """"Tests for a request with a password shorter than 8 characters."""
        signup_data = {
            "user": {
                "username": "Mary Jane",
                "email": "maryjane@gmail.com",
                "password": "Mary1234",
                "callback_url": "https://medium.com"
            }
        }
        payload = {
            "email": "maryjane@gmail.com",
            "callback_url": "https://www.youtube.com/"

        }
        token = TokenHandler().create_verification_token(payload)
        short_password_data = {
            "user_password": {
                "password": "try",
                "confirm_password": "try",
                "token": token
            }
        }

        short_password_data_response = {"errors": {
            "password": ["Password should be at least 8 characters long"]
        }
        }
        self.client.post(self.register_url, signup_data, format='json')
        response = self.client.put(self.url, short_password_data,
                                   format='json')
        self.assertEqual(response.data, short_password_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_long_password(self):
        """"Tests for a request with a password longer than 128 characters."""
        signup_data = {
            "user": {
                "username": "Mary Jane",
                "email": "maryjane@gmail.com",
                "password": "Mary1234",
                "callback_url": "https://medium.com"
            }
        }
        payload = {
            "email": "maryjane@gmail.com",
            "callback_url": "https://www.youtube.com/"

        }
        token = TokenHandler().create_verification_token(payload)
        long_password_data = {
            "user_password": {
                "password": "try"*50,
                "confirm_password": "try"*50,
                "token": token
            }
        }

        long_password_data_response = {"errors": {
            "password": ["Password should not be longer than 128 characters"]
        }
        }
        self.client.post(self.register_url, signup_data, format='json')
        response = self.client.put(self.url, long_password_data,
                                   format='json')
        self.assertEqual(response.data, long_password_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_matching_passwords(self):
        """"Tests for a request with passwords that do not match."""
        signup_data = {
            "user": {
                "username": "Mary Jane",
                "email": "maryjane@gmail.com",
                "password": "Mary1234",
                "callback_url": "https://medium.com"
            }
        }
        payload = {
            "email": "maryjane@gmail.com",
            "callback_url": "https://www.youtube.com/"

        }
        token = TokenHandler().create_verification_token(payload)
        password_data = {
            "user_password": {
                "password": "try12qw3ew45r",
                "confirm_password": "trytrfds234erwdsq",
                "token": token
            }
        }

        self.client.post(self.register_url, signup_data, format='json')
        user = get_object_or_404(User, email="maryjane@gmail.com")
        user_id = user.id
        token_data = {
            "user": user_id,
            "token": token
        }
        serializer = PasswordResetTokenSerializer(data=token_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        password_data_response = {"message": "Passwords do not Match"}
        response = self.client.put(self.url, password_data,
                                   format='json')
        self.assertEqual(response.data, password_data_response)
