from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, force_authenticate

class RegistrationViewTest(TestCase):
    """This class defines tests for the RegistrationView class"""
    def setUp(self):
        self.user1 = {"user":
                            {"email": "user1@mail.com",
                            "username": "user1",
                            "password": "password"}
                    }

    def test_user_can_register(self):
        """Test if a user is able to register"""
        client = APIClient()
        response = client.post(reverse('authentication:register'), self.user1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class LoginViewTest(TestCase):
    """This class defines tests for the LoginView class"""
    def setUp(self):
        self.user1 = {"user":
        {"email": "user1@mail.com",
         "username": "user1",
          "password": "password"}
          }
        self.user1_credentials = {"user": {
            "email": "user1@mail.com",
            "password": "password"
        }}

    def test_registered_user_can_log_in(self):
        """Test if a registered user can log in"""
        client = APIClient()
        client.post(reverse('authentication:register'), self.user1, format='json')
        response = client.post(reverse('authentication:login'), self.user1_credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserRetrieveUpdateAPITest(TestCase):
    """This class defines tests for the UserRetrieveUpdateAPIView"""
    def test_if_we_can_retrieve_user_list(self):
        """Test if a logged in user can retrieve a user list"""
        user1 = {"user":
        {"email": "user1@mail.com",
            "username": "user1",
            "password": "password"}
            }
        client = APIClient()
        client.post(reverse('authentication:register'), user1, format='json')
        client.login(email="user1@mail.com", password="password")
        response = client.get(reverse('authentication:get users'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_if_we_can_update_user_data(self):
        """Test if we can update the user data"""
        user1 = {"user":
        {"email": "user1@mail.com",
            "username": "user1",
            "password": "password"}
            }

        update_info = {"user": {
            "email": "user1@mail.com",
            "bio": "I love to be tested",
            "values": "EPIC"
        }}
        client = APIClient()
        client.post(reverse('authentication:register'), user1, format='json')
        client.login(email="user1@mail.com", password="password")
        response = client.put(reverse('authentication:get users'), update_info, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
