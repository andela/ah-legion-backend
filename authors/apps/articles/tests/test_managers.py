from django.test import TestCase
from django.contrib.auth import get_user_model

from authors.apps.core.factories import UserFactory

from ..factories import ArticleFactory
from ..models import ThreadedComment


class  CommentActiveObjectsManagerTests(TestCase):

    def setUp(self):
        self.user1 = UserFactory.create()
        self.user2 = UserFactory.create()
        self.article1 = ArticleFactory.create(author=self.user1)
        self.article2 = ArticleFactory.create(author=self.user2)

    def test_fetching_only_active_comments(self):
        comment1 = ThreadedComment.objects.create(author=self.user1.profile,
                                         article=self.article1)
        comment2 = ThreadedComment.objects.create(author=self.user1.profile,
                                         article=self.article1)
        comments = [comment1, comment2]
        self.assertQuerysetEqual(
            ThreadedComment.active_objects.all_comments(),
            [repr(comment) for comment in comments]
        )
        comment2.is_active = False
        comment2.save()
        comments = [comment1]
        self.assertQuerysetEqual(
            ThreadedComment.active_objects.all_comments(),
            [repr(comment) for comment in comments]
        )

    def test_fetching_comments_by_author(self):
        comment1 = ThreadedComment.objects.create(author=self.user1.profile,
                                         article=self.article1)
        comment2 = ThreadedComment.objects.create(author=self.user2.profile,
                                         article=self.article1)
        comments = [comment1]
        self.assertQuerysetEqual(
            ThreadedComment.active_objects.for_author(self.user1.profile),
            [repr(comment) for comment in comments]
        )
        comments = [comment2]
        self.assertQuerysetEqual(
            ThreadedComment.active_objects.for_author(self.user2.profile),
            [repr(comment) for comment in comments]
        )

    def test_fetching_comments_by_article(self):
        comment1 = ThreadedComment.objects.create(author=self.user1.profile,
                                         article=self.article1)
        comment2 = ThreadedComment.objects.create(author=self.user1.profile,
                                         article=self.article2)
        comments = [comment1]
        self.assertQuerysetEqual(
            ThreadedComment.active_objects.for_article(article=self.article1),
            [repr(comment) for comment in comments]
        )
        comments = [comment2]
        self.assertQuerysetEqual(
            ThreadedComment.active_objects.for_article(article=self.article2),
            [repr(comment) for comment in comments]
        )

    def test_fetching_comments_by_comment(self):
        comment1 = ThreadedComment.objects.create(author=self.user1.profile,
                                         article=self.article1)
        comment2 = ThreadedComment.objects.create(author=self.user1.profile,
                                         article=self.article2, comment=comment1)
        comment3 = ThreadedComment.objects.create(author=self.user1.profile,
                                         article=self.article2, comment=comment1)
        comments = [comment2, comment3]
        self.assertQuerysetEqual(
            ThreadedComment.active_objects.for_comment(comment=comment1),
            [repr(comment) for comment in comments]
        )
        comment4 = ThreadedComment.objects.create(author=self.user1.profile,
                                         article=self.article2, comment=comment1)
        comments = [comment2, comment3, comment4]
        self.assertQuerysetEqual(
            ThreadedComment.active_objects.for_comment(comment=comment1),
            [repr(comment) for comment in comments]
        )
