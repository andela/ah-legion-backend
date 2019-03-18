from datetime import datetime, timedelta

import jwt

from django.conf import settings

from rest_framework import exceptions

from django.core.mail import EmailMessage
from django.template.loader import render_to_string


class TokenHandler:
    """This class contains the methods for creating custom
    tokens for users"""

    def create_verification_token(self, payload):
        """
        Create a JWT token to be sent in the verification
        email url
        """

        if not isinstance(payload, dict):
            raise TypeError('Payload must be a dictionary!')

        token_expiry = datetime.now() + timedelta(hours=12)

        try:
            token = jwt.encode({
                'email': payload['email'],
                'callback_url': payload['callback_url'],
                'exp': int(token_expiry.strftime('%s'))},
                settings.SECRET_KEY, algorithm='HS256')
            return token.decode('utf-8')

        except KeyError:
            return "Please provide email and callback_url"

    def validate_token(self, token):
        """
        Validate provided token. The email encoded in the token
        should be equal to the email of the user instance being
        passed.
        """

        try:
            decoded_token = jwt.decode(
                token, settings.SECRET_KEY, algorithm='HS256')

        except jwt.exceptions.ExpiredSignatureError:
            msg = 'Your token has expired. Make a new token and try again'
            raise exceptions.AuthenticationFailed(msg)

        except Exception:
            msg = 'Error. Could not decode token!'
            return msg

        return decoded_token

    def send_password_reset_link(self, to_email, token, callback_url):
        domain = settings.DOMAIN
        html_content = render_to_string('password_reset.html',
                                        {'callback_url': callback_url,
                                         'token': token, 'domain': domain})
        subject = 'Reset your Author\'s Haven Password'
        from_email = settings.EMAIL_HOST_USER
        msg = EmailMessage(subject, html_content, from_email, [to_email])
        msg.content_subtype = 'html'
        msg.send()

