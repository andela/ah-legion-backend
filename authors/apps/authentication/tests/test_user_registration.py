from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


class RegistrationTestCase(APITestCase):
    url = reverse('authentication:register')

    def test_user_registration(self):
        """Test for a valid user registration."""
        signup_data = {
            "user": {
                "username": "Mary",
                "email": "mary@gmail.com",
                "password": "Mary1234"
            }
        }

        response = self.client.post(self.url, signup_data, format='json')
        signup_data_response = {
            "email": "mary@gmail.com", "username": "Mary"
        }
        self.assertEqual(response.data, signup_data_response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_blank_username(self):
        """Test for user registration with a blank username."""
        blank_username_data = {
            "user": {
                "username": "",
                "email": "john@gmail.com",
                "password": "John1234"
            }
        }
        blank_username_data_response = {"errors": {
            "username": ["Username field cannot be blank"]
        }
        }
        response = self.client.post(self.url, blank_username_data, format='json')
        self.assertEqual(response.data, blank_username_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_username_field(self):
        """Test for user registration without a username field."""
        no_username_field_data = {
            "user": {
                "email": "john@gmail.com",
                "password": "John1234"
            }
        }
        no_username_field_data_response = {"errors": {
            "username": ["Username is required"]
        }
        }
        response = self.client.post(self.url, no_username_field_data, format='json')
        self.assertEqual(response.data, no_username_field_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_existing_username(self):
        """Test for user registration with an existing username."""
        username_data = {
            "user": {
                "username": "Mary",
                "email": "mary@gmail.com",
                "password": "John1234"
            }
        }
        existing_username_data = {
            "user": {
                "username": "Mary",
                "email": "maryg@gmail.com",
                "password": "John1234"
            }
        }
        existing_username_data_response = {"errors": {
            "username": ["A user with this username already exists"]
        }
        }
        self.client.post(self.url, username_data, format='json')
        response = self.client.post(self.url, existing_username_data, format='json')
        self.assertEqual(response.data, existing_username_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blank_email(self):
        """Test for user registration with a blank email."""
        blank_email_data = {
            "user": {
                "username": "John",
                "email": "",
                "password": "John1234"
            }
        }
        blank_email_data_response = {"errors": {
            "email": ["Email field cannot be blank"]
        }
        }
        response = self.client.post(self.url, blank_email_data, format='json')
        self.assertEqual(response.data, blank_email_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_email_field(self):
        """Test for user registration without an email field."""
        no_email_field_data = {
            "user": {
                "username": "John",
                "password": "John1234"
            }
        }
        no_email_field_data_response = {"errors": {
            "email": ["Email is required"]
        }
        }
        response = self.client.post(self.url, no_email_field_data, format='json')
        self.assertEqual(response.data, no_email_field_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email(self):
        """"Test for user registration with an invalid email."""
        invalid_email_data = {
            "user": {
                "username": "John",
                "email": "johngmail.com",
                "password": "John1234"
            }
        }
        invalid_email_data_response = {"errors": {
            "email": ["Please enter a valid email address"]
        }
        }
        response = self.client.post(self.url, invalid_email_data, format='json')
        self.assertEqual(response.data, invalid_email_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_existing_email(self):
        """Test for user registration with an existing email."""
        email_data = {
            "user": {
                "username": "John",
                "email": "mary@gmail.com",
                "password": "John1234"
            }
        }
        existing_email_data = {
            "user": {
                "username": "John Snow",
                "email": "mary@gmail.com",
                "password": "John1234"
            }
        }
        existing_email_data_response = {"errors": {
            "email": ["A user with this email already exists"]
        }
        }
        self.client.post(self.url, email_data, format='json')
        response = self.client.post(self.url, existing_email_data, format='json')
        self.assertEqual(response.data, existing_email_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blank_password(self):
        """Test for user registration with a blank password."""
        blank_password_data = {
            "user": {
                "username": "John",
                "email": "john@gmail.com",
                "password": ""
            }
        }
        blank_password_data_response = {"errors": {
            "password": ["Password field cannot be blank"]
        }
        }
        response = self.client.post(self.url, blank_password_data, format='json')
        self.assertEqual(response.data, blank_password_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_password_field(self):
        """Test for user registration with a blank password."""
        no_password_field_data = {
            "user": {
                "username": "John",
                "email": "john@gmail.com"
            }
        }
        no_password_field_data_response = {"errors": {
            "password": ["Password is required"]
        }
        }
        response = self.client.post(self.url, no_password_field_data, format='json')
        self.assertEqual(response.data, no_password_field_data_response)

    def test_not_alphanumeric_password(self):
        """"Test for user registration with a password that is not alphanumeric."""
        not_alphanumeric_password_data = {
            "user": {
                "username": "John",
                "email": "john@gmail.com",
                "password": "@John1234"
            }
        }
        not_alphanumeric_password_data_response = {"errors": {
            "password": ["Password should be alphanumeric"]
        }
        }
        response = self.client.post(self.url, not_alphanumeric_password_data, format='json')
        self.assertEqual(response.data, not_alphanumeric_password_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_password(self):
        """"Test for user registration with a password shorter than 8 characters."""
        not_alphanumeric_password_data = {
            "user": {
                "username": "Sally",
                "email": "sally@gmail.com",
                "password": "sally"
            }
        }
        not_alphanumeric_password_data_response = {"errors": {
            "password": ["Password should be at least 8 characters long"]
        }
        }
        response = self.client.post(self.url, not_alphanumeric_password_data, format='json')
        self.assertEqual(response.data, not_alphanumeric_password_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_long_password(self):
        """"Test for user registration with a password longer than 128 characters."""
        not_alphanumeric_password_data = {
            "user": {
                "username": "Sally",
                "email": "sally@gmail.com",
                "password": 30 * "pellentesque"
            }
        }
        not_alphanumeric_password_data_response = {"errors": {
            "password": ["Password should not be longer than 128 characters"]
        }
        }
        response = self.client.post(self.url, not_alphanumeric_password_data, format='json')
        self.assertEqual(response.data, not_alphanumeric_password_data_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
