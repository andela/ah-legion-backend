from django.test import TestCase

from authors.apps.core.factories import UserFactory

from ..factories import ArticleFactory
from ..models import Snapshot, ThreadedComment, Bookmark


class CommentMethodTests(TestCase):

    def setUp(self):
        self.user1 = UserFactory.create()
        self.article1 = ArticleFactory.create(author=self.user1.profile)

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


class CommentSnapshotSignalTests(TestCase):

    def setUp(self):
        self.user1 = UserFactory.create()
        self.article1 = ArticleFactory.create(author=self.user1.profile)

    def test_snapshot_is_saved_only_when_a_comment_is_edited(self):
        body = "testing comment"
        comment = ThreadedComment.objects.create(
            author=self.user1.profile, article=self.article1, body=body)
        self.assertNotEqual(comment.snapshots.all(), [])
        self.assertFalse(comment.edited)
        comment.body = "edited this comment"
        comment.save()
        snapshots = Snapshot.objects.filter(comment=comment)
        self.assertQuerysetEqual(comment.snapshots.all(),
                                 [repr(snap) for snap in snapshots])
        self.assertEqual(snapshots.first().body, comment.body)
        same_comment = ThreadedComment.objects.get(id = comment.id)
        self.assertTrue(same_comment.edited)
