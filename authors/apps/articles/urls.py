from django.urls import path
from .views import (
    CreateArticleView, GetArticlesView,
    GetAnArticleView, UpdateAnArticleView
)
app_name = 'articles'

urlpatterns = [
    path(
        'articles/create', CreateArticleView.as_view(),
        name="create_article"
    ),
    path('articles', GetArticlesView.as_view(), name="get_article"),
    path(
        'articles/<slug:slug>', GetAnArticleView.as_view(),
        name="get_an_article"
    ),
    path(
        'articles/<slug:slug>/edit', UpdateAnArticleView.as_view(),
        name="update_an_article"
    )
]
