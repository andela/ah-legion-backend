import factory

from authors.apps.core.factories import UserFactory

from .models import Article


class ArticleFactory(factory.DjangoModelFactory):

    class Meta:
        model = Article

    title = "Article title"
    draft = "a draft body"
    author = factory.SubFactory(UserFactory)
