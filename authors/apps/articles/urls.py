from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('create/', views.CreateArticleView.as_view(),
         name="create_article"),
    path('', views.GetArticlesView.as_view(), name="get_article"),
    path('<slug:slug>/', views.GetAnArticleView.as_view(),
         name="get_an_article"),
    path('<slug:slug>/edit/', views.UpdateAnArticleView.as_view(),
         name="update_an_article"),
    path('<slug:slug>/publish/', views.PublishAnArticleView.as_view(),
         name="publish_an_article"),
    path('<slug:slug>/like/', views.CreateRetrieveLikeView.as_view(),
         name="create_like"),
    path('<slug:slug>/like/<int:pk>/', views.UpdateDeleteLikeView.as_view(),
         name="update_like"),
    path('<slug:slug>/likes/', views.GetArticleLikesView.as_view(),
         name="get_likes"),
    path('<slug:article_slug>/comments/', views.CommentListCreateView.as_view(),
         name="list_create_comments"),
    path('<slug:article_slug>/comments/<pk>/',
         views.CommentRetrieveEditDeleteView.as_view(),
         name="comment"),
    path('<slug:slug>/likes/',
         views.GetArticleLikesView.as_view(), name="get_likes"),
    path('<slug:slug>/favorite/',
         views.FavoriteView.as_view(), name="favorite"),

    path('user/favorites/',
         views.GetUserFavoritesView.as_view(), name="get_favorites"),
    path('<slug:slug>/rate/',
         views.RatingView.as_view(), name="rate"),
    path('<slug:slug>/ratings/',
         views.GetRatingView.as_view(), name="get_rating"),
    path('<slug:slug>/bookmark/',
         views.BookmarkView.as_view(), name="create_bookmark"),
    path('user/bookmarks/',
         views.GetUserBookmarksView.as_view(), name="get_bookmarks"),
]
