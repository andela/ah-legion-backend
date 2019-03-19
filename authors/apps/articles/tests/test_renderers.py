from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIRequestFactory

from authors.apps.core.factories import UserFactory


from ..factories import ArticleFactory
from ..models import ThreadedComment
from ..renderers import CommentJSONRenderer
from ..serializers import ThreadedCommentOutputSerializer


class CommentRendererTest(TestCase):

    def setUp(self):
        self.user1 = UserFactory.create()
        self.article1 = ArticleFactory.create(author=self.user1)
        self.factory = APIRequestFactory()

    def test_comment_json_renderer(self):
        """Test the comment renderer renders comments as expected."""
        comment1 = ThreadedComment.objects.create(author=self.user1.profile,
                                                article=self.article1)
        comment2 = ThreadedComment.objects.create(author=self.user1.profile,
                                                article=self.article1)
        request = self.factory.get(reverse("articles:list_create_comments",
                                           args=[self.article1.slug]),
                                   format='json')
        serializer = ThreadedCommentOutputSerializer(
            comment1, context={"current_user": self.user1})
        rendered_comment = CommentJSONRenderer().render(serializer.data)
        self.assertIn("Comment", rendered_comment)
        comments = ThreadedComment.active_objects.all_comments()
        serializer2 = ThreadedCommentOutputSerializer(
            comments, many=True, context={"current_user": self.user1})
        rendered_comments = CommentJSONRenderer().render(serializer2.data)
        self.assertIn("Comments", rendered_comments)
