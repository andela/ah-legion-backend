from django.test import TestCase

from authors.apps.articles.models import Tag, Article, ReportArticle
from authors.apps.authentication.models import User
from authors.apps.articles.serializers import TheArticleSerializer

class ArticleModelTestCase(TestCase):

    def setUp(self):
        self.user_one = User.objects.create(
            email = "jake@jake.jake",
            password =  "jakejake",
            username = "Jake"
        )
        self.article_one = Article.objects.create(
            title = "I am the OG",
            body = "This is an article by the OG",
            author = self.user_one.profile
        )
        self.report1 = ReportArticle.objects.create(
            message = "this is the worst article I have ever read",
            article = self.article_one,
            reporter = self.user_one
        )


    def test_article_creation(self):
        
        self.assertEqual(
            self.article_one.__str__(),
            "I am the OG"
        )
    def test_report_string_representation(self):
        """ test for the value returned by __str__ """
        self.assertEqual(str(self.report1), "this is the worst article I have ever read")

    def test_get_username(self):
        username = self.report1.get_username()
        self.assertEqual(username, "Jake")


class  TagModelTestCase(TestCase):

    def setUp(self):
        self.user_one = User.objects.create(
            email = "jake@jake.jake",
            password =  "jakejake",
            username = "Jake"
        )
        self.article_one = Article.objects.create(
            title = "I am the OG",
            body = "This is an article by the OG",
            author = self.user_one.profile
        )

    def test_tag_creation(self):
        my_tag = Tag.objects.create(tag = "Etomovich")
        my_tag.save()
        self.assertEqual(
            my_tag.slug,
            "etomovich"
        )

    def test_delete_tags_without_articles(self):
        my_tag = Tag(tag = "Etomovich")
        my_tag.save()
        remove_tag = my_tag._remove_tags_without_articles("Etomovich")
        self.assertTrue(remove_tag)

    def test_fail_to_delete_tags_with_articles(self):
        a_tag = Tag.objects.create(tag = "Andela")
        self.article_one.tags.add(a_tag)
        remove_tag = a_tag._remove_tags_without_articles("Andela")
        self.assertFalse(remove_tag)
        remove_tag = a_tag._remove_tags_without_articles("Etomovich")
        self.assertFalse(remove_tag)
