import os
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .article_tests_base_class import ArticlesBaseTest
from .test_data import *
from authors.apps.articles.views import *


class LikeDislikeArticleTestCase(ArticlesBaseTest):
    """Test like and dislike of articles"""

    def test_like_article(self):
        """Test like"""
        response = self.client.post(self.like_article_url,
                                    like_data, **self.header_user1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test invalid slug
        response = self.client.post('/api/articles/invalid-slug/like/',
                                    like_data, **self.header_user1, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Test already liked article
        response = self.client.post(self.like_article_url,
                                    like_data, **self.header_user1, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_like(self):
        """Test like"""
        response = self.client.get(self.like_article_url,
                                   **self.header_user1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.post(self.like_article_url,
                         like_data, **self.header_user1, format='json')
        response1 = self.client.get(
            self.like_article_url, **self.header_user1)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        # Test invalid slug
        response = self.client.get('/api/articles/invalid-slug/like/',
                                   **self.header_user1)
        detail = "This article has not been found."
        self.assertEqual(response.data.get('detail'), detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_like(self):
        """Test update like to dislike or vice versa"""
        # test updating like that does not exist
        response1 = self.client.patch(self.like_article_url + str(3) + '/',
                                      like_data, **self.header_user1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_404_NOT_FOUND)
        # Create like
        response = self.client.post(self.like_article_url,
                                    like_data, **self.header_user1, format='json')
        like_id = response.data.get('id')
        response1 = self.client.patch(self.like_article_url + str(like_id) + '/',
                                      like_data, **self.header_user1, format='json')
        self.assertContains(response1, 'is_like', status_code=200)
        # Trying to update while not an owner
        response = self.client.patch(self.like_article_url + str(like_id) + '/',
                                     like_data, **self.header_user2, format='json')
        detail = "This user does not own this like"
        self.assertEqual(response.data.get('detail'), detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_like(self):
        """Test update like to dislike or vice versa"""
        # test updating like that does not exist
        response1 = self.client.delete(self.like_article_url + str(3) + '/',
                                       like_data, **self.header_user1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.post(self.like_article_url,
                                    like_data, **self.header_user1, format='json')
        like_id = response.data.get('id')

        # Trying to update while not an owner
        response = self.client.delete(self.like_article_url + str(like_id) + '/',
                                      like_data, **self.header_user2, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response1 = self.client.delete(self.like_article_url + str(like_id) + '/',
                                       like_data, **self.header_user1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_204_NO_CONTENT)

    def test_method_not_allowed(self):
        """Test module not found class"""
        response = self.client.put(self.like_article_url,
                                       like_data, **self.header_user1, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_likes(self):
        """Test get likes count endpoint"""
        self.client.post(self.like_article_url,
                         like_data, **self.header_user1, format='json')

        response = self.client.get('/api/articles/' + self.slug + '/likes/',
                                   **self.header_user1)
        self.assertEqual(response.data.get('likes'), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test invalid slug
        response = self.client.get('/api/articles/invalid-slug/likes/',
                                   **self.header_user1)
        detail = "This article has not been found."
        self.assertEqual(response.data.get('detail'), detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
