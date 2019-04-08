from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from .test_data import *
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article


class ArticlesBaseTest(APITestCase):
    """Sets up tests for features related to articles"""

    def setUp(self):
        client = APIClient()
        self.user1 = User.objects.create_user(
            username='Moracha', email="jratcher@gmail.com", password='password')
        self.user1.is_verified = True
        self.user1.save()
        self.user2 = User.objects.create_user(
            username='Josh', email='joshmoracha@gmail.com', password='password')
        self.user2.is_verified = True
        self.user2.save()
        self.user1_credentials = client.post(reverse('authentication:login'),
                                             user1, format='json')
        self.user2_credentials = client.post(reverse('authentication:login'),
                                             user2, format='json')
        user1_token = self.user1_credentials.data.get('token')
        user2_token = self.user2_credentials.data.get('token')
        self.header_user1 = {
            'HTTP_AUTHORIZATION': f'Bearer {user1_token}'
        }
        self.header_user2 = {
            'HTTP_AUTHORIZATION': f'Bearer {user2_token}'
        }
        response = client.post(reverse('articles:create_article'),
                               article, **self.header_user1, format='json')
       
        self.slug = response.data.get('slug')
        #Publish article
        retrieved_article = Article.objects.filter(slug=self.slug).first()
        retrieved_article.published = True
        retrieved_article.save()
        self.like_article_url = '/api/articles/{}/like/'.format(self.slug)
        self.favorite_article_url = '/api/articles/{}/favorite/'.format(self.slug)
        self.get_favorites_url = reverse('articles:get_favorites')
        self.rate_url = '/api/articles/{}/rate/'.format(self.slug)
        self.get_rate_url = '/api/articles/{}/ratings/'.format(self.slug)
        self.non_existent_article = '/api/articles/hi/rate/'
        self.get_non_existent_article = '/api/articles/hi/ratings/'
        self.article_rating = '/api/articles/'
        self.bookmark_article_url = '/api/articles/{}/bookmark/'.format(self.slug)
