from django.test import TestCase

from authors.apps.core.factories import UserFactory

from ..factories import ArticleFactory
from ..models import ThreadedComment


class CommentMethodTests(TestCase):

    def setUp(self):
        self.user1 = UserFactory.create()
        self.article1 = ArticleFactory.create(author=self.user1)

    def test_comment_string_representation(self):
        body = "comments and stuff "
        comment = ThreadedComment.objects.create(
            author=self.user1.profile, article=self.article1, body=body)
        self.assertEqual(str(comment),
                         f"{str(self.user1.profile)}: comments and stuff ...")

    def test_comment_soft_deletion(self):
        comment = ThreadedComment.objects.create(author=self.user1.profile,
                                        article=self.article1)
        self.assertEqual(comment.is_active, True)
        comment.soft_delete()
        self.assertEqual(comment.is_active, False)

    def test_comment_undoing_soft_deletion(self):
        comment = ThreadedComment.objects.create(author=self.user1.profile,
                                        article=self.article1)
        self.assertEqual(comment.is_active, True)
        comment.soft_delete()
        self.assertEqual(comment.is_active, False)
        comment.undo_soft_deletion()
        self.assertEqual(comment.is_active, True)
