from django.test import TestCase

from rest_framework.serializers import ValidationError

from authors.apps.authentication.models import User
from authors.apps.authentication.serializers import (LoginSerializer,
                                                     RegistrationSerializer,
                                                     UserSerializer)


class RegistrationSerializerTests(TestCase):
    """This class defines tests for the RegistrationSerializer class"""
    def setUp(self):
        self.user_data = {
            "username": "bob",
            "email": "bob@email.com",
            "password": "hardpassword"
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
        user.save()
        serializer = LoginSerializer(data=login_data)

        returned_user_data = serializer.validate(login_data)
        self.assertEqual({
            "email": "bob@email.com",
            "username": "bob"},
            returned_user_data
        )


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

