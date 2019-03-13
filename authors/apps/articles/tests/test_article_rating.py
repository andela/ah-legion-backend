from rest_framework import status

from .article_tests_base_class import ArticlesBaseTest
from .test_data import *
from authors.apps.articles.models import Rating, Article


class ArticleRatingTestCase(ArticlesBaseTest):
    """Test like and dislike of articles"""

    def test_valid_rating(self):
        """Tests for a valid rating post request."""
        res = self.client.post(self.rate_url,
                               valid_rate_data1, **self.header_user2, format='json')
        self.assertEqual(res.data, valid_data_rasponse)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_rate_non_existent_article(self):
        """Tests a post request for a non-existent article."""
        res = self.client.post(self.non_existent_article,
                               valid_rate_data1, **self.header_user2, format='json')
        self.assertEqual(res.data, non_existent_article_response)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_author_rating(self):
        """Tests for a post request where the user is also the article author."""
        res = self.client.post(self.rate_url,
                               valid_rate_data1, **self.header_user1, format='json')
        self.assertEqual(res.data, author_rating_data_response)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_rating_twice(self):
        """Tests for a post request by a user to rate an article they have already rated."""
        self.client.post(self.rate_url,
                         valid_rate_data1, **self.header_user2, format='json')
        res = self.client.post(self.rate_url,
                               valid_rate_data1, **self.header_user2, format='json')
        self.assertEqual(res.data, rating_twice_data_response)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_reviews(self):
        """Tests for a valid get request to fetch all reviews."""
        self.client.post(self.rate_url,
                         valid_rate_data1, **self.header_user2, format='json')
        res = self.client.get(self.get_rate_url, **self.header_user2, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_no_reviews(self):
        """Tests for a get request to fetch non-existent reviews."""
        self.client.post(self.rate_url,
                         valid_rate_data2, **self.header_user2, format='json')
        res = self.client.get(self.get_rate_url, **self.header_user2, format='json')
        self.assertEqual(res.data, no_review_data_response)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_article_not_rated(self):
        """Tests for an article that has not been rated when getting articles."""
        res = self.client.get(self.article_rating, **self.header_user2, format='json')
        self.assertEqual(res.data['results'][0]['average_rating'], no_ratings_data_response)

    def test_get_non_existent_article(self):
        """Tests for a request to get the rating of a non-existent article."""
        res = self.client.get(self.get_non_existent_article, **self.header_user2, format='json')
        self.assertEqual(res.data, non_existent_article_response)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_rated_article(self):
        """Tests for an article that has been rated when getting articles."""
        self.client.post(self.rate_url,
                         valid_rate_data1, **self.header_user2, format='json')
        res = self.client.get(self.article_rating, **self.header_user2, format='json')
        self.assertEqual(res.data['results'][0]['average_rating'], 2.0)

    def test_update_rating(self):
        """Tests for a valid request to update a rating."""
        self.client.post(self.rate_url,
                         valid_rate_data1, **self.header_user2, format='json')
        res = self.client.put(self.rate_url, update_rating_data, **self.header_user2, format='json')
        self.assertEqual(res.data, update_rating_data_response)
        
    def test_update_not_rated_article(self):
        """Tests for a valid request to update a rating."""
        self.client.post(self.rate_url,
                         valid_rate_data1, **self.header_user1, format='json')
        res = self.client.put(self.rate_url, update_rating_data, **self.header_user2, format='json')
        self.assertEqual(res.data, not_rated_data_response)

    def test_update_non_existent_article(self):
        """Tests for a valid request to update a rating."""
        res = self.client.put(self.non_existent_article, update_rating_data, **self.header_user2, format='json')
        self.assertEqual(res.data, non_existent_article_response)

    def test_model_representation(self):
        retrieved_article = Article.objects.filter(slug=self.slug).first()
        retrieved_article.published = True
        retrieved_article.save()
        self.rating = Rating.objects.create(article=retrieved_article, user= self.user2,
                                            value=1, review="no way")
        self.assertEqual(str(self.rating), "This is rating no: 1")
