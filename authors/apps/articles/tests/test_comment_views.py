import json

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient, force_authenticate
from rest_framework.test import APIRequestFactory

from authors.apps.core.factories import UserFactory

from ..factories import ArticleFactory
from ..models import Article, ThreadedComment, CommentLike
from ..views import (CommentListCreateView, CommentRetrieveEditDeleteView,
                     CommentLikeCreateDeleteView)


class CommentListCreateViewTest(TestCase):

    def setUp(self):
        self.user1 = UserFactory.create()
        self.article = ArticleFactory.create(author=self.user1)
        self.factory = APIRequestFactory()

    def test_author_can_create_article_comments(self):
        """Test an author can coment on an article."""
        view = CommentListCreateView.as_view()
        profile_id = self.user1.id
        new_comment = {
            "body": "This is my comment"
        }
        request = self.factory.post(
            reverse("articles:list_create_comments", args=[self.article.slug]),
            new_comment, format='json')
        force_authenticate(request, user=self.user1)
        response = view(request, article_slug=self.article.slug)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_catching_malformed_comment_creation_data(self):
        view = CommentListCreateView.as_view()
        request = self.factory.post(
            reverse("articles:list_create_comments", args=[self.article.slug]),
            format='json')
        force_authenticate(request, user=self.user1)
        response = view(request, article_slug=self.article.slug)
        expected_data = {
            "body": ["This field is required."]
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_author_can_coment_on_comments(self):
        """Test an author can coment on a comment."""
        comment = ThreadedComment.objects.create(
            author=self.user1.profile, article=self.article)
        view = CommentListCreateView.as_view()
        new_comment = {
            "body": "This is a comment's comment"
        }
        url = reverse("articles:comment", args=[self.article.slug, comment.pk])
        request = self.factory.post(url, new_comment, format='json')
        force_authenticate(request, user=self.user1)
        response = view(request, article_slug=self.article.slug, pk=comment.pk)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['body'],
                         "This is a comment's comment")

    def test_author_only_coment_on_article_comments(self):
        """Test an author cannot coment on a comment of a comment."""
        comment = ThreadedComment.objects.create(
            author=self.user1.profile, article=self.article)
        comment_of_comment = ThreadedComment.objects.create(
            author=self.user1.profile, article=self.article, comment=comment)
        view = CommentRetrieveEditDeleteView.as_view()
        new_comment = {
            "body": "This is a comment on a comment of a comment"
        }
        url = reverse("articles:comment",
                      args=[self.article.slug, comment_of_comment.pk])
        request = self.factory.post(url, new_comment, format='json')
        force_authenticate(request, user=self.user1)
        response = view(request, article_slug=self.article.slug,
                        pk=comment_of_comment.pk)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_comment_on_comment(self):
        user = get_user_model().objects.create_user(email="bob@email.com",
                                                    password="pass",
                                                    username="bob")
        user.is_verified = True
        user.save()
        article = ArticleFactory.create(author=user)
        comment = ThreadedComment.objects.create(author=user.profile,
                                               article=article)
        client = APIClient()
        data = {"body": "the comment"}
        login_data = {
            "user": {
                "email": user.email,
                "password": "pass"
            }
        }
        response1 = client.post(reverse("authentication:login"), login_data,
                                format='json')
        token = response1.data['token']
        headers = {
            'HTTP_AUTHORIZATION': f'Bearer {token}'
        }
        url = reverse("articles:comment", args=[article.slug, comment.pk])
        response = client.post(url, data, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['body'], 'the comment')

    def test_coment_on_comments_bad_request(self):
        """Test an author comenting on a comment with bad data."""
        comment = ThreadedComment.objects.create(
            author=self.user1.profile, article=self.article)
        view = CommentListCreateView.as_view()
        request = self.factory.post(
            reverse("articles:comment", args=[self.article.slug, comment.pk]),
            format='json')
        force_authenticate(request, user=self.user1)
        response = view(request, article_slug=self.article.slug, pk=comment.pk)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_viewing_comments_on_a_non_existent_article(self):
        view = CommentListCreateView.as_view()
        request = self.factory.get(reverse("articles:list_create_comments",
                                           kwargs={'article_slug': 'i-dont-exist'}))
        response = view(request, article_slug='i-dont-exit')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_viewing_a_list_of_comments(self):
        view = CommentListCreateView.as_view()
        article_slug = self.article.slug
        request = self.factory.get(
            reverse("articles:list_create_comments", args=[article_slug]),
            format='json')
        response = view(request, article_slug=article_slug)
        self.assertEqual(response.data, [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieving_a_comment(self):
        comment = ThreadedComment.objects.create(
            author=self.user1.profile, article=self.article)
        view = CommentRetrieveEditDeleteView.as_view()
        request = self.factory.get(
            reverse("articles:comment", args=[self.article.slug, comment.pk]),
            format='json')
        response = view(request,
                        article_slug=self.article.slug, pk=comment.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_updating_a_comment_with_put(self):
        comment = ThreadedComment.objects.create(
            author=self.user1.profile, article=self.article)
        view = CommentRetrieveEditDeleteView.as_view()
        comment_update = {"body": "Ive been udated!!"}
        request = self.factory.put(
            reverse("articles:comment", args=[self.article.slug, comment.pk]),
            comment_update, format='json')
        force_authenticate(request, user=self.user1)
        response = view(request,
                        article_slug=self.article.slug, pk=comment.pk)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_updating_a_comment_of_a_commentwith_put(self):
        comment = ThreadedComment.objects.create(
            author=self.user1.profile, article=self.article)
        comment2 = ThreadedComment.objects.create(
            author=self.user1.profile, article=self.article, comment=comment)
        view = CommentRetrieveEditDeleteView.as_view()
        comment_update = {"body": "Ive been udated!!"}
        request = self.factory.put(
            reverse("articles:comment", args=[self.article.slug, comment2.pk]),
            comment_update, format='json')
        force_authenticate(request, user=self.user1)
        response = view(request,
                        article_slug=self.article.slug, pk=comment2.pk)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_updating_a_comment_with_patch(self):
        comment = ThreadedComment.objects.create(
            author=self.user1.profile, article=self.article)
        view = CommentRetrieveEditDeleteView.as_view()
        comment_update = {"body": "Ive been udated!!"}
        request = self.factory.patch(
            reverse("articles:comment", args=[self.article.slug, comment.pk]),
            comment_update, format='json')
        force_authenticate(request, user=self.user1)
        response = view(request,
                        article_slug=self.article.slug, pk=comment.pk)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        request2 = self.factory.patch(
            reverse("articles:comment", args=[self.article.slug, comment.pk]),
            comment_update, format='json')
        response2 = view(request2,
                        article_slug=self.article.slug, pk=comment.pk)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

    def test_deleting_a_comment(self):
        comment = ThreadedComment.objects.create(
            author=self.user1.profile, article=self.article)
        view = CommentRetrieveEditDeleteView.as_view()
        request = self.factory.delete(
            reverse("articles:comment", args=[self.article.slug, comment.pk]),
            format='json')
        force_authenticate(request, user=self.user1)
        response = view(request, article_slug=self.article.slug, pk=comment.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        request2 = self.factory.get(
            reverse("articles:comment", args=[self.article.slug, comment.pk]),
            format='json')
        force_authenticate(request2, user=self.user1)
        response2 = view(request2, article_slug=self.article.slug, pk=comment.pk)
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)


class CommentLikeDeleteViewTests(TestCase):

    def setUp(self):
        self.user1 = UserFactory.create()
        self.article = ArticleFactory.create(author=self.user1)
        self.factory = APIRequestFactory()


    def test_liking_a_comment(self):
        comment = ThreadedComment.objects.create(
            author=self.user1.profile, article=self.article)
        view = CommentLikeCreateDeleteView.as_view()
        request = self.factory.put(
            reverse("articles:comment_likes", args=[self.article.slug, comment.pk]),
            format='json')
        force_authenticate(request, user=self.user1)
        response = view(request, article_slug=self.article.slug, pk=comment.pk)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_unliking_a_comment(self):
        comment = ThreadedComment.objects.create(
            author=self.user1.profile, article=self.article)
        like = CommentLike.objects.create(comment=comment, user=self.user1)
        view = CommentLikeCreateDeleteView.as_view()
        request = self.factory.delete(
            reverse("articles:comment_likes", args=[self.article.slug, comment.pk]),
            format='json')
        force_authenticate(request, user=self.user1)
        response = view(request, article_slug=self.article.slug, pk=comment.pk)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
