from django.test import TestCase

from rest_framework.serializers import ValidationError
from rest_framework import exceptions

from authors.apps.authentication.models import User
from authors.apps.authentication.serializers import (LoginSerializer,
                                                     RegistrationSerializer,
                                                     UserSerializer, 
                                                     CreateEmailVerificationSerializer)



class RegistrationSerializerTests(TestCase):
    """This class defines tests for the RegistrationSerializer class"""

    def setUp(self):
        self.user_data = {
            "username": "bob",
            "email": "bob@email.com",
            "password": "hardpassword",
            "callback_url": "http://www.example.com"
        }

    def test_create_method(self):
        """Test if the create method for the RegistrationSerializer works"""
        serializer = RegistrationSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        new_user = serializer.save()
        self.assertIsInstance(new_user, User)


class LoginSerializerTests(TestCase):
    """This class defines tests for the LoginSerializer class"""

    def test_validating_login_serializer_without_email(self):
        """Test if users can login without providing an email"""
        login_data = {"password": "hardpassword"}
        serializer = LoginSerializer(data=login_data)

        with self.assertRaises(ValidationError) as e:
            serializer.validate(login_data)
        self.assertEqual(e.exception.detail[0],
                         "An email address is required to log in.")

    def test_validating_login_serializer_without_password(self):
        """Test if users can login without providing an email"""
        login_data = {"email": "bob@email.com"}
        serializer = LoginSerializer(data=login_data)

        with self.assertRaises(ValidationError) as e:
            serializer.validate(login_data)

        self.assertEqual(e.exception.detail[0],
                         "A password is required to log in.")

    def test_validating_login_serializer_of_unexistant_user(self):
        """Test if non-existant users are able to log in"""
        login_data = {"email": "bob@email.com", "password": "harpassword"}
        serializer = LoginSerializer(data=login_data)

        with self.assertRaises(ValidationError) as e:
            serializer.validate(login_data)

        self.assertEqual(e.exception.detail[0],
                         "A user with this email and password was not found.")

    def test_creating_validating_correct_email_and_password(self):
        """Test if the validate method works when valid information is passed"""
        login_data = {"email": "bob@email.com", "password": "hardpassword"}
        user = User.objects.create_user(username="bob", email="bob@email.com",
                                        password="hardpassword")
        user.is_verified = True
        user.save()
        serializer = LoginSerializer(data=login_data)

        returned_user_data = serializer.validate(login_data)
        self.assertEqual({
            "email": "bob@email.com",
            "username": "bob",
            'token': user.token},
            returned_user_data
        )

    def test_unverified_user_cannot_log_in(self):
        """Users who have not verified their accounts should not be able to log in"""
        login_data = {"email": "bob@email.com", "password": "hardpassword"}
        user = User.objects.create_user(username="bob", email="bob@email.com",
                                        password="hardpassword")
        user.save()
        serializer = LoginSerializer(data=login_data)

        with self.assertRaises(ValidationError) as e:
            serializer.validate(login_data)

        self.assertEqual(e.exception.detail[0],
                         "Please verify your account to proceed.")


class UserSerializersTests(TestCase):
    """This class defines tests for the UserSerializer class"""

    def setUp(self):
        self.user = User.objects.create_user(username="bob", email="bob@email.com",
                                             password="hardpassword")
        self.user.save()
        self.serializer = UserSerializer()

    def test_updating_user_information_including_password(self):
        """Test if we can update user information, including the password"""
        user_password = self.user.password
        user_update_data = {"username": "bobby", "email": "bobby@email.com",
                            "password": "otherpassword"}
        updated_user = self.serializer.update(self.user, user_update_data)
        self.assertEqual(updated_user.username, "bobby")
        self.assertEqual(updated_user.email, "bobby@email.com")
        self.assertNotEqual(updated_user.password, user_password)

    def test_updating_user_information_excluding_password(self):
        """Test if we can update user information but the password is not changed"""
        user_data = {"username": "robert", "email": "robert@email.com"}
        user_password = self.user.password
        updated_user = self.serializer.update(self.user, user_data)
        self.assertEqual(updated_user.username, "robert")
        self.assertEqual(updated_user.email, "robert@email.com")
        self.assertEqual(updated_user.password, user_password)


class CreateEmailVerificationSerializerTests(TestCase):
    """This class defines the tests for our CreateEmailVerificationSerializer"""

    def test_user_must_pass_registered_email(self):
        """
        Users should only be able to get tokens when they send an email that has been registered
        """

        data = {'email': 'unregistered@mail.com', 'username': 'unregistered',
                'callback_url': 'http://www.example.com'}
        serializer = CreateEmailVerificationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        with self.assertRaises(ValidationError) as e:
            serializer.create_payload(data)

        self.assertEqual(e.exception.detail[0],
                         "No user with this email address is registered.")

    def test_user_must_pass_correct_email_address_and_username(self):
        """The user must pass correct username and email in order to get a verification token"""

        User.objects.create_user(username='real_user',
                                 email='real@mail.com', password='password')

        data = {'email': 'real@mail.com', 'username': 'unregistered',
                'callback_url': 'http://www.example.com'}
        serializer = CreateEmailVerificationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        with self.assertRaises(ValidationError) as e:
            serializer.create_payload(data)

        self.assertEqual(e.exception.detail[0],
                         "Your username and email don't match.")

    def test_serializer_returns_payload_when_user_passes_valid_data(self):
        """
        The serializer should return a payload containing 
        the user data if the user provides valid data
        """

        User.objects.create_user(username='real_user',
                                 email='real@mail.com', password='password')

        data = {'email': 'real@mail.com', 'username': 'real_user',
                'callback_url': 'http://www.example.com'}
        serializer = CreateEmailVerificationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        output = serializer.create_payload(data)
        self.assertEqual(output, data)
        
    def test_serializer_failure_because_verified_user_requests_token(self):
        """Verified users should not be able to request new verification tokens"""

        user = User.objects.create_user(username='test', email='test@mail.com', password='password')
        user.is_verified = True
        user.save()

        data = {'email': 'test@mail.com',
                'username': 'test',
                'callback_url': 'http://www.example.com'}
        
        serializer = CreateEmailVerificationSerializer(data=data)
        self.assertTrue(serializer.is_valid)

        with self.assertRaises(exceptions.ValidationError) as e:
            serializer.create_payload(data)
        self.assertEqual(e.exception.detail[0], 'This user has already been verified')
