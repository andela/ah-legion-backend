from django.test import TestCase, Client
from django.urls import reverse

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

        self.email1 = 'test@gmail.com'
        self.username1 = 'brian'
        self.password1 = 'testuserpass'

        # create a user that will be logged in
        self.user = User.objects.create_user(
            self.username, self.email, self.password)
        
        self.user1 = User.objects.create_user(
            self.username1, self.email1, self.password1)

        # verify a user's account and save
        self.user.is_verified = True
        self.user.save()
        

        self.data = {
            'user': {
                'username': self.username,
                'email': self.email,
                'password': self.password,
                'callback_url': 'http://www.example.com'
            }
        }
        self.data1 = {
            'user': {
                'username': 'brian',
                'email': 'brian@testing.com',
                'password': 'veryverystrongpassword',
            }
        }

        self.updated_data = {

            'username': "newname",
            'email': "another@email.com",
            'password': "otherpaswword",
            'bio': 'i like classical music'

        }
        self.errornious_updated_data = {
            "website": "notavalidurlforawebsiteman"
        }
        self.image_link = {
            "image": "cats.jpg"
        }
        self.bad_image_link = {
            "image": "cats.pdf"
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
            reverse("authentication:login"),
            data=json.dumps(self.data), content_type='application/json')
        token = response.json()['user']['token']
        return token

    def register_user(self, user_details_dict):
        """ Register anew user to the system

        Args:
            user_details_dict: a dictionary with username, email, password of the user

        Returns: an issued post request to the user registration endpoint
        """
        return self.test_client.post(
            reverse("authentication:register"),
            data=json.dumps(user_details_dict), content_type='application/json')
    
    def follow_user(self, username, token):
        """This method sends a follow request to a user"""
        follow_url = reverse("profiles:follow-unfollow", kwargs={'username': username})
        response = self.client.post(
            follow_url,
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        return response

    def unfollow_user(self, username, token):
        """This method sends a follow request to a user"""
        follow_url = reverse("profiles:follow-unfollow", kwargs={'username': username})
        response = self.client.delete(
            follow_url,
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        return response

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
        self.assertEqual(
            response.json()['user']['profile']['bio'], 'i like classical music')

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

    def test_if_renderer_catches_errors(self):
        """ test is an error is caught by profile json renderer """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        self.register_user(self.data)
        response = self.test_client.put(
            "/api/user/", **headers, content_type='application/json', data=json.dumps(self.errornious_updated_data))

        self.assertEqual(response.json()['errors']['profile']['website'], [
                         "Enter a valid URL."])

    def test_if_image_uploads_successfully(self):
        """ test if an profile image uploads successfully """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        self.register_user(self.data)
        response = self.test_client.put(
            "/api/user/", **headers, content_type='application/json', data=json.dumps(self.image_link))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user']['profile']['image_url'],
                         "https://res.cloudinary.com/dbsri2qtr/image/upload/c_fill,h_150,w_100/cats")

    def test_if_one_can_upload_pdf_as_profile_image(self):
        """ test if an profile image uploads successfully """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        self.register_user(self.data)
        response = self.test_client.put(
            "/api/user/", **headers, content_type='application/json', data=json.dumps(self.bad_image_link))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['user']['image'],
            "Only '.png', '.jpg', '.jpeg' files are accepted")
        
    def test_successful_follow(self):
        """Test whether API user can follow another successfully"""
        token = self.login_a_user()
        self.register_user(self.data1)
        response = self.follow_user("brian", token)
        self.assertEqual(response.json()['profile']['message'],
                         "You are now following brian")
        self.assertEqual(response.status_code, 200)

    def test_follow_unavailable_user(self):
        """Test whether API user can follow an unavailable user"""
        token = self.login_a_user()
        response = self.follow_user("neverheardofuser", token)
        self.assertEqual(response.json()['profile']['detail'],
                         "The requested profile does not exist.")
        self.assertEqual(response.status_code, 400)

    def test_follow_yourself(self):
        """Test whether API user can follow oneself"""
        token = self.login_a_user()
        response = self.follow_user("testing12", token)
        self.assertEqual(response.json()['errors'],
                         ["Nice try, you cannot follow yourself"])
        self.assertEqual(response.status_code, 400)
    
    def test_unfollow_yourself(self):
        """Test whether an existing user may unfollow themseves """
        token = self.login_a_user()
        response = self.unfollow_user("testing12", token)
        self.assertEqual(response.json()['errors'],
                         ["Nice try, that is not possible"])
        self.assertEqual(response.status_code, 400)


    def test_follow_user_already_followed(self):
        """Test whether API user can follow a user they already follow"""
        token = self.login_a_user()
        self.register_user(self.data1)
        self.follow_user("brian", token)
        response = self.follow_user("brian", token)
        self.assertEqual(response.json()['profile']['error'],
                         "You are already following brian")
        self.assertEqual(response.status_code, 406)

    def test_successful_unfollow(self):
        """Test whether API user can unfollow a follower successfully"""
        token = self.login_a_user()
        self.register_user(self.data1)
        self.follow_user('brian', token)
        response = self.unfollow_user('brian', token)
        self.assertEqual(response.json()['profile']['message'],
                         "You just unfollowed brian")
        self.assertEqual(response.status_code, 200)

    def test_unfollow_unavailable_user(self):
        """Test whether API user can unfollow a follower successfully"""
        token = self.login_a_user()
        response = self.unfollow_user("UnavailableUser", token)
        self.assertEqual(response.json()['profile']['detail'],
                         "The requested profile does not exist.")
        self.assertEqual(response.status_code, 400)

    def test_unfollow_nonfollower(self):
        """Test whether API user can unfollow a user they don't follow"""
        token = self.login_a_user()
        self.register_user(self.data1)
        response = self.unfollow_user("brian", token)
        self.assertEqual(response.json()['profile']['error'],
                         "You are not following brian")
        self.assertEqual(response.status_code, 406)

    def test_get_following(self):
        """Test whether API user can view follow list successfully"""
        self.register_user(self.data1)
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        self.follow_user("brian", token)
        response = self.test_client.get(
            "/api/profiles/brian/following/", **headers, content_type='application/json')
        self.assertIsInstance(response.json()['Followers'], list)
        self.assertIsInstance(response.json()['Following'], list)
        self.assertEqual(response.status_code, 200)

    def test_get_following_for_non_existant_user(self):
        """Test following for a non existing profile """
        token = self.login_a_user()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + token}
        response = self.test_client.get(
            "/api/profiles/veryveryfunnyusername/following/", **headers, content_type='application/json')
        self.assertEqual(response.json()['detail'],
                         "The requested profile does not exist.")
        self.assertEqual(response.status_code, 400)
