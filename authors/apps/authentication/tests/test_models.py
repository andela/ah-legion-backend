from django.test import TestCase

from authors.apps.authentication.models import User


class UserManagerTest(TestCase):
    """This class defines tests for UserManager class"""

    def test_successfully_create_user(self):
        """"""
        user1 = User.objects.create_user(
            username="user1", email="user1@mail.com", password="password")
        self.assertIsInstance(user1, User)

    def test_registration_failure_due_to_no_username(self):
        """Test if user can register without a username"""
        with self.assertRaises(TypeError) as e:
            User.objects.create_user(
                email="user1@mail.com", username=None, password="password")
        self.assertEqual(str(e.exception), 'Users must have a username.')

    def test_registration_failure_due_to_no_email(self):
        """Test if a user can register without an email"""
        with self.assertRaises(TypeError) as e:
            User.objects.create_user(
                username="user2", email=None, password="password")
        self.assertEqual(str(e.exception), 'Users must have an email address.')

    def test_registration_superuser_fail_due_to_no_password(self):
        """Test if a superuser can register without a password"""
        with self.assertRaises(TypeError) as e:
            User.objects.create_superuser(
                username="superuser", email="superuser@mail.com", password=None)
        self.assertEqual(str(e.exception), 'Superusers must have a password.')

    def test_successfully_create_superuser(self):
        """Test if we can successfully create a superuser"""
        user1 = User.objects.create_superuser(
            username="superuser", email="superuser@mail.com", password="password")
        self.assertTrue(user1.is_superuser)
        self.assertTrue(user1.is_staff)


class UserTest(TestCase):
    """This class defines tests for user models"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user", email="user@mail.com", password="password")

    def test_user_string_representation(self):
        """Test if proper string representation is returned for users"""
        self.assertEqual(str(self.user1), "user@mail.com")

    def test_get_full_name(self):
        """Test if proper full name is returned for users"""
        self.assertEqual(self.user1.get_full_name, "user")

    def test_get_short_name(self):
        """Test if proper short name is returned for users"""
        self.assertEqual(self.user1.get_short_name(), "user")
