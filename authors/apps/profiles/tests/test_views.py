from django.test import TestCase, Client

import json

from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile
from authors.apps.profiles.renderers import ProfileJSONRenderer


class TestProfileViews(TestCase):
    def setUp(self):
        """ Funtion to setup some code that will be needed for unittests """
        self.email = 'boomboom@gmail.com'
        self.username = 'testing12'
        self.password = 'testuserpass'

        # create a user that will be logged in
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        # verify a user's account and save
        self.user.is_verified = True
        self.user.save()

        self.data = {
            'user': {
                'username': self.username,
                'email': self.email,
                'password': self.password,
            }
        }
        self.updated_data = {
            'user': {
                'username': "newname",
                'email': "another@email.com",
                'password': "otherpaswword",
            }
        }

        self.test_client = Client()

        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}

    def tearDown(self):
        pass

    def login_a_user(self):
        """
        Reusable function to login a user
        """

        response = self.test_client.post(
            "/api/users/login/", data=json.dumps(self.data), content_type='application/json')
        token = response.json()['user']['token']
        return token

    def register_user(self, user_details_dict):
        """ Register anew user to the system

        Args:
            user_details_dict: a dictionary with username, email, password of the user

        Returns: an issued post request to the user registration endpoint
        """
        return self.test_client.post(
            "/api/users/", data=json.dumps(user_details_dict), content_type='application/json')

    @property
    def token(self):
        return self.login_a_user()

    def test_retrieve_profile(self):
        """ test for the retrive profile endpoint """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.get(
            "/api/profiles/{}/".format(self.username), **headers, content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_update_existing_profie(self):
        """ test for updating exisiting user profile"""
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        self.register_user(self.data)
        response = self.test_client.put(
            "/api/user/", **headers, content_type='application/json', data=json.dumps(self.updated_data))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user']['email'], "another@email.com")
        self.assertEqual(response.json()['user']['username'], "newname")

    def test_list_all_profiles(self):
        """ test for checking if app returns all available profiles """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.client.get(
            "/api/profiles/", **headers, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_non_existing_profile(self):
        """ test for checking if app catches non-existing profile error """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.client.get(
            "/api/profiles/serdgddddadscw/", **headers, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['profile']['detail'], "The requested profile does not exist.")
