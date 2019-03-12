from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    name = 'authors.apps.articles'

    def ready(self):
        from . import signals # noqa
