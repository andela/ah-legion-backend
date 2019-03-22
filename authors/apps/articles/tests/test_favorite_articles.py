import os
from django.urls import reverse
from rest_framework import status
from .article_tests_base_class import ArticlesBaseTest
from .test_data import *
from authors.apps.articles.views import *


class FavoriteArticleTestCase(ArticlesBaseTest):
    """Test favoriting an article functionality"""

    def test_favorite_article(self):
        """Test favorite article"""
        response = self.client.post(
            self.favorite_article_url, **self.header_user1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Test already liked article
        response = self.client.post(self.favorite_article_url,
                                    like_data, **self.header_user1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Test invalid slug
        response = self.client.post('/api/articles/invalid-slug/favorite/',
                                    like_data, **self.header_user1, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_favorite(self):
        """Test get favorite"""
        response = self.client.get(self.favorite_article_url,
                                   **self.header_user1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.post(self.favorite_article_url,
                         like_data, **self.header_user1, format='json')
        response1 = self.client.get(
            self.favorite_article_url, **self.header_user1)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        # Test invalid slug
        response = self.client.get('/api/articles/invalid-slug/favorite/',
                                   **self.header_user1)
        detail = "This article has not been found."
        self.assertEqual(response.data.get('detail'), detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_favorites(self):
        """Test get favorites endpoint"""
        self.client.post(self.favorite_article_url, **self.header_user1)

        response = self.client.get('/api/articles/user/favorites/',
                                   **self.header_user1)
        self.assertEqual(len(response.data.get('favorites')), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_favorite(self):
        """Test delete favorite"""
        # test delete favorite that does not exist
        response1 = self.client.delete(
            self.favorite_article_url, **self.header_user1)
        self.assertEqual(response1.status_code, status.HTTP_404_NOT_FOUND)

        self.client.post(self.favorite_article_url,
                         **self.header_user1)

        response1 = self.client.delete(
            self.favorite_article_url, **self.header_user1)
        self.assertEqual(response1.status_code, status.HTTP_204_NO_CONTENT)
        # Test with non existent slug
        response = self.client.delete('/api/articles/invalid-slug/favorite/',
                                   **self.header_user1)
        detail = "This article has not been found."
        self.assertEqual(response.data.get('detail'), detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
