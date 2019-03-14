from datetime import date, timedelta

from django.test import TestCase
from django.conf import settings
from rest_framework import exceptions

import jwt

from authors.apps.core.utils import TokenHandler


class TestTokenHandler(TestCase):
    """Test if TokenHandler returns tokens as expected"""

    def test_token_is_created(self):
        """We test whether we are able to create a token"""

        payload = {
            'email': 'test@mail.com',
            'callback_url': 'http://www.example.com'
        }

        token = TokenHandler().create_verification_token(payload)
        # a valid token should be decoded
        self.assertTrue(TokenHandler().validate_token(token))

    def test_decoding_failure_because_payload_is_not_dictionary(self):
        """The payload to be encoded should be a dictionary"""

        payload = ['just a list']

        with self.assertRaises(TypeError) as e:
            TokenHandler().create_verification_token(payload)
        self.assertEqual(str(e.exception), 'Payload must be a dictionary!')

    def test_token_can_only_be_encoded_if_neccessary_keys_are_passed(self):
        """For a token to be created, we need the `email` and `callback_url` to be provided"""

        error = TokenHandler().create_verification_token({})
        self.assertEqual(error, 'Please provide email and callback_url')

    def test_expired_token_results_in_an_error(self):
        """If a token expires, users should not be verified by providing it"""

        token_expiry = date.today() - timedelta(1)

        payload = {
            'email': 'test@mail.com',
            'callback_url': 'http://www.example.com'
        }

        token = jwt.encode({
            'email': payload['email'],
            'callback_url': payload['callback_url'],
            'exp': int(token_expiry.strftime('%s'))
        },
            settings.SECRET_KEY, algorithm='HS256')

        with self.assertRaises(exceptions.AuthenticationFailed) as e:
            TokenHandler().validate_token(token)

        self.assertEqual(
            str(e.exception), 'Your token has expired. Make a new token and try again')

    def test_an_invalid_token_cannot_be_decoded(self):
        """If a user passes an invalid jwt token, it should not be decoded"""

        token = ''
        res = TokenHandler().validate_token(token)

        self.assertEqual(res, 'Error. Could not decode token!')
