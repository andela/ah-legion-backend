import os
from django.urls import reverse
from rest_framework import status
from .article_tests_base_class import ArticlesBaseTest
from .test_data import *
from authors.apps.articles.views import *


class BookmarkArticleTestCase(ArticlesBaseTest):
    """Test bookmarking an article functionality"""

    def test_bookmark_article(self):
        """Test bookmark article"""
        response = self.client.post(
            self.bookmark_article_url, **self.header_user1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Test already bookmarked article
        response = self.client.post(self.bookmark_article_url,
                                    like_data, **self.header_user1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Test invalid slug
        response = self.client.post('/api/articles/invalid-slug/bookmark/',
                                    like_data, **self.header_user1, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_bookmark(self):
        """Test get bookmark"""
        response = self.client.get(self.bookmark_article_url,
                                   **self.header_user1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.post(self.bookmark_article_url,
                        **self.header_user1, format='json')
        response1 = self.client.get(
            self.bookmark_article_url, **self.header_user1)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        # Test invalid slug
        response = self.client.get('/api/articles/invalid-slug/bookmark/',
                                   **self.header_user1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_bookmarks(self):
        """Test get bookmarks endpoint"""
        self.client.post(self.bookmark_article_url, **self.header_user1)

        response = self.client.get('/api/articles/user/bookmarks/',
                                   **self.header_user1)
        self.assertEqual(len(response.data.get('bookmarks')), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_bookmark(self):
        """Test delete bookmark"""
        # test delete bookmark that does not exist
        response1 = self.client.delete(
            self.bookmark_article_url, **self.header_user1)
        self.assertEqual(response1.status_code, status.HTTP_404_NOT_FOUND)

        self.client.post(self.bookmark_article_url,
                         **self.header_user1)

        response1 = self.client.delete(
            self.bookmark_article_url, **self.header_user1)
        self.assertEqual(response1.status_code, status.HTTP_204_NO_CONTENT)
        # Test with non existent slug
        response = self.client.delete('/api/articles/invalid-slug/bookmark/',
                                      **self.header_user1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
