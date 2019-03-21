from .serializers import (ArticleCommentInputSerializer,
                          CommentCommentInputSerializer,
                          EmbededCommentOutputSerializer,
                          LikesSerializer,
                          TheArticleSerializer,
                          ThreadedCommentOutputSerializer,
                          FavoriteSerializer, RatingSerializer,
                          ArticleRatingSerializer)
from .renderers import ArticleJSONRenderer, CommentJSONRenderer
from .permissions import CanCreateComment, CanEditComment
from .models import Article, Like, ThreadedComment, Favorite, Rating, Tag
from authors.apps.core.views import BaseManageView
from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination


class CreateArticleView(mixins.CreateModelMixin,
                        generics.GenericAPIView):
    queryset = Article.objects.all()
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = (TheArticleSerializer)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        payload = request.data.get('article', {})
        the_tags = payload.get("tagList", None)
        tags_pk = []
        if the_tags:
            the_tags = payload.pop("tagList")
            tag_object = Tag()
            for item in the_tags:
                my_tag = tag_object._create_tag(item)
                tags_pk.append(my_tag.pk)
            payload["tags"] = tags_pk

        # Decode token
        this_user = request.user
        payload['author'] = this_user.pk

        serializer = TheArticleSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetArticlesView(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Article.objects.all()
    permission_classes = (AllowAny,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = (TheArticleSerializer)
    pagination_class = LimitOffsetPagination

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        # Decode token
        reply_not_found = {}
        paginator = self.pagination_class()
        published_articles = Article.objects.filter(
            published=True, activated=True)
        page = paginator.paginate_queryset(published_articles, request)

        if (len(published_articles) < 1):
            reply_not_found["detail"] = "No articles have been found."
            return Response(
                reply_not_found,
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class GetAnArticleView(mixins.RetrieveModelMixin,
                       generics.GenericAPIView):
    queryset = Article.objects.all()
    permission_classes = (AllowAny,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = (TheArticleSerializer)

    def get(self, request, slug):
        '''Get a single article'''
        found_article = Article.objects.filter(
            slug=slug, published=True,
            activated=True
        ).first()

        if found_article is not None:
            serialized = self.serializer_class(found_article)
            return Response(
                serialized.data,
                status=status.HTTP_200_OK
            )
        not_found = {}
        not_found['detail'] = "This article has not been found."
        return Response(
            not_found,
            status=status.HTTP_404_NOT_FOUND
        )


class UpdateAnArticleView(mixins.UpdateModelMixin,
                          generics.GenericAPIView):
    queryset = Article.objects.all()
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = (TheArticleSerializer)
    lookup_field = "slug"

    def _edit_article(self, request, the_data):
        if self.get_object().author == request.user:
            if self.get_object().activated is False:
                invalid_entry = {
                    "detail": "This article does not exist."
                }
                return Response(
                    invalid_entry,
                    status=status.HTTP_404_NOT_FOUND
                )

            article_obj = self.get_object()
            this_tags = the_data.get("tagList", None)
            tags_pk = []
            if this_tags:
                this_tags = the_data.pop("tagList")
                tag_object = Tag()
                for item in this_tags:
                    the_tag = tag_object._create_tag(item)
                    tags_pk.append(the_tag.pk)
                the_data["tags"] = tags_pk

            serialized = self.serializer_class(
                article_obj, data=the_data, partial=True
            )
            serialized.is_valid(raise_exception=True)
            self.perform_update(serialized)
            if "activated" in the_data.keys() \
                    and the_data["activated"] is False:
                deleted_entry = {
                    "detail": "This article has been deleted."
                }
                return Response(
                    deleted_entry,
                    status=status.HTTP_200_OK
                )
            return Response(
                serialized.data,
                status=status.HTTP_200_OK
            )

        not_found = {
            "detail": "You are not the owner of the article."
        }
        return Response(
            not_found,
            status=status.HTTP_401_UNAUTHORIZED
        )

    def put(self, request, *args, **kwargs):
        '''This method method updates field of model article'''
        my_data = request.data.get('article', {})
        return self._edit_article(request, my_data)

    def delete(self, request, *args, **kwargs):
        '''This method performs a soft deletion of an article.'''
        soft_delete = {"activated": False}
        return self._edit_article(request, soft_delete)

    def patch(self, request, *args, **kwargs):
        '''This method is used to publish an article.'''
        new_data = self.get_object().draft
        if new_data is not None:
            publish_data = {
                "body": new_data,
                "published": True
            }
            return self._edit_article(request, publish_data)
        no_edit = {}
        no_edit["detail"] = "Draft has no data"
        return Response(
            no_edit,
            status=status.HTTP_400_BAD_REQUEST
        )


class CreateLikeView(generics.CreateAPIView):
    """This class creates a new like or dislike"""
    permission_classes = (IsAuthenticated,)
    serializer_class = LikesSerializer

    def create(self, request, slug):
        """Creates a like"""
        data = request.data
        article = Article.objects.filter(
            slug=slug, published=True, activated=True).first()
        if article is None:
            not_found = {
                "detail": "This article has not been found."
            }
            return Response(data=not_found, status=status.HTTP_404_NOT_FOUND)

        like = Like.objects.filter(
            user_id=request.user.pk, article_id=article.id).first()
        if like is not None:
            like_found = {
                "detail": "Article already liked or disliked, \
                    use another route to update."
            }
            return Response(data=like_found, status=status.HTTP_400_BAD_REQUEST)

        data['article_id'] = article.id
        data['user_id'] = request.user.pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetLikeView(generics.RetrieveAPIView):
    """Fetch like or dislike for an article"""
    permission_classes = (IsAuthenticated,)
    queryset = Like.objects.all()

    def get(self, request, slug):
        article = Article.objects.filter(
            slug=slug, published=True, activated=True).first()
        if article is None:
            not_found = {
                "detail": "This article has not been found."
            }
            return Response(data=not_found, status=status.HTTP_404_NOT_FOUND)
        like = Like.objects.filter(
            user_id=request.user.pk, article_id=article.id).first()
        if like is None:
            no_like = {
                "detail": "This user has neither liked \
                    nor disliked the article."
            }
            return Response(data=no_like, status=status.HTTP_404_NOT_FOUND)
        like_data = {"id": like.id,
                     "article_id": like.article_id.id,
                     "user_id": like.user_id.id
                     }
        return Response(data=like_data, status=status.HTTP_200_OK)


class UpdateLikeView(generics.UpdateAPIView):
    """Perfom update on likes"""
    permission_classes = (IsAuthenticated,)
    serializer_class = LikesSerializer
    queryset = Like.objects.all()

    def patch(self, request, *args, **kwargs):
        like_id = kwargs['pk']
        like = Like.objects.filter(id=like_id).first()
        if like:
            like_owner_id = like.user_id.id
            if like_owner_id != request.user.id:
                message = {
                    "detail": "This user does not own this like"
                }
                return Response(data=message, status=status.HTTP_403_FORBIDDEN)
        return self.partial_update(request, *args, **kwargs)


class DeleteLikeView(generics.DestroyAPIView):
    """Delete like"""
    permission_classes = (IsAuthenticated,)
    serializer_class = LikesSerializer
    queryset = Like.objects.all()

    def delete(self, request, *args, **kwargs):
        like_id = kwargs['pk']
        like = Like.objects.filter(id=like_id).first()
        if like:
            like_owner_id = like.user_id.id
            if like_owner_id != request.user.id:
                message = {"detail": "This user does not own this like"}
                return Response(data=message, status=status.HTTP_403_FORBIDDEN)
        return self.destroy(request, *args, **kwargs)


class CreateRetrieveLikeView(BaseManageView):
    """Handles create and retrieve likes"""
    VIEWS_BY_METHOD = {
        'POST': CreateLikeView.as_view,
        'GET': GetLikeView.as_view,
    }


class UpdateDeleteLikeView(BaseManageView):
    """Handles update and retrieve a like"""
    VIEWS_BY_METHOD = {
        'PATCH': UpdateLikeView.as_view,
        'DELETE': DeleteLikeView.as_view,
    }


class GetArticleLikesView(APIView):
    """Gets all articles' likes and dislikes"""
    permission_classes = (AllowAny,)

    def get(self, request, slug):
        article = Article.objects.filter(
            slug=slug, published=True, activated=True).first()
        if article is None:
            not_found = {
                "detail": "This article has not been found."
            }
            return Response(data=not_found, status=status.HTTP_404_NOT_FOUND)
        likes_queryset = Like.objects.filter(
            is_like=True, article_id=article.id)
        dislikes_queryset = Like.objects.filter(
            is_like=False, article_id=article.id)
        dislikes_count = dislikes_queryset.count()
        likes_count = likes_queryset.count()
        likes_dislikes = {
            "likes": likes_count,
            "dislikes": dislikes_count,
        }
        return Response(data=likes_dislikes, status=status.HTTP_200_OK)


class FetchArticleMixin:
    """
    Provide get_article() method that returns
    the article from the url.
    """

    def get_article(self):
        article = get_object_or_404(Article, slug=self.kwargs['article_slug'])
        return article


class CommentListCreateView(FetchArticleMixin, APIView):
    """
    Create new comment.
    """
    renderer_classes = (CommentJSONRenderer,)
    permission_classes = (CanCreateComment,)

    def get(self, request, *args, **kwargs):
        article = self.get_article()
        comments = ThreadedComment.active_objects.for_article(article)
        article_comments = comments.filter(comment__isnull=True)
        serializer = ThreadedCommentOutputSerializer(
            article_comments, context={'current_user': request.user}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        article = self.get_article()
        user = request.user
        data["article"] = article.id
        data["author"] = user.id
        serializer = ArticleCommentInputSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        response_serializer = ThreadedCommentOutputSerializer(
            comment, context={'current_user': request.user})
        return Response(response_serializer.data,
                        status=status.HTTP_201_CREATED)


class CommentRetrieveEditDeleteView(FetchArticleMixin,
                                    generics.GenericAPIView):
    renderer_classes = (CommentJSONRenderer,)
    permission_classes = (CanEditComment,)

    def get_queryset(self):
        article = self.get_article()
        return ThreadedComment.active_objects.for_article(article)

    def get(self, request, *args, **kwargs):
        """Return single a comment."""
        comment = self.get_object()
        serializer = ThreadedCommentOutputSerializer(
            comment, context={'current_user': request.user})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Create a comment on another comment."""
        data = request.data.copy()
        commented_comment = self.get_object()
        if commented_comment.for_comment():
            msg = {'message': 'Sorry, you cannot make'
                   ' a comment on this comment'}
            return Response(msg, status.HTTP_400_BAD_REQUEST)
        user = request.user
        article = self.get_article()
        data["comment"] = commented_comment.id
        data["author"] = user.profile.id
        data["article"] = article.id
        serializer = CommentCommentInputSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        response_serializer = EmbededCommentOutputSerializer(
            comment, context={'current_user': request.user})
        return Response(response_serializer.data, status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """Edit all fields in a comment."""
        data = request.data.copy()
        comment = self.get_object()
        data["article"] = comment.article.id
        data["author"] = comment.author.id
        if comment.for_comment():
            data["comment"] = comment.comment.id
        serializer = ArticleCommentInputSerializer(comment, data=data)
        serializer.is_valid(raise_exception=True)
        updated_comment = serializer.save()
        response_serializer = ThreadedCommentOutputSerializer(
            updated_comment, context={'current_user': request.user})
        return Response(response_serializer.data,
                        status=status.HTTP_202_ACCEPTED)

    def patch(self, request, *args, **kwargs):
        """Edit one field in a comment."""
        data = request.data.copy()
        comment = self.get_object()
        serializer = ArticleCommentInputSerializer(comment, data=data,
                                                   partial=True)
        serializer.is_valid(raise_exception=True)
        updated_comment = serializer.save()
        response_serializer = ThreadedCommentOutputSerializer(
            updated_comment, context={'current_user': request.user})
        return Response(response_serializer.data,
                        status=status.HTTP_202_ACCEPTED)

    def delete(self, request, *args, **kwargs):
        """Soft delete a comment."""
        comment = self.get_object()
        comment.soft_delete()
        return Response({"detail": "comment deleted"},
                        status=status.HTTP_200_OK)


class FavoriteView(generics.CreateAPIView):
    """This class creates a new favorite"""
    permission_classes = (IsAuthenticated,)
    serializer_class = FavoriteSerializer

    def post(self, request, slug):
        """Creates a favorite"""
        data = request.data
        article = Article.objects.filter(
            slug=slug, published=True, activated=True).first()
        if article is None:
            not_found = {
                "detail": "This article has not been found."
            }
            return Response(data=not_found, status=status.HTTP_404_NOT_FOUND)

        favorite = Favorite.objects.filter(
            user_id=request.user.pk, article_id=article.id).first()
        if favorite is not None:
            favorite_found = {
                "detail": "Article already in favorites."
            }
            return Response(data=favorite_found,
                            status=status.HTTP_400_BAD_REQUEST)

        data['article_id'] = article.id
        data['user_id'] = request.user.pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = serializer.data
        data['detail'] = 'Article added to favorites.'
        return Response(data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        article = Article.objects.filter(
            slug=kwargs['slug'], published=True, activated=True).first()
        if article is None:
            not_found = {
                "detail": "This article has not been found."
            }
            return Response(data=not_found, status=status.HTTP_404_NOT_FOUND)
        favorite = Favorite.objects.filter(
            article_id=article.id, user_id=request.user.pk).first()
        if favorite:
            message = {"detail": "Article removed from favorites"}
            favorite.delete()
            return Response(data=message, status=status.HTTP_204_NO_CONTENT)
        not_found = {"detail": "Article not favorite"}
        return Response(not_found, status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        article = Article.objects.filter(
            slug=kwargs['slug'], published=True, activated=True).first()
        if article is None:
            not_found = {
                "detail": "This article has not been found."
            }
            return Response(data=not_found, status=status.HTTP_404_NOT_FOUND)
        favorite = Favorite.objects.filter(
            article_id=article.id, user_id=request.user.pk).first()
        if favorite:
            serializer = self.serializer_class(favorite)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        not_found = {"detail": "Article not favorite"}
        return Response(not_found, status.HTTP_404_NOT_FOUND)


class GetUserFavoritesView(APIView):
    """Gets all users' favorite articles"""
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        favorites_queryset = Favorite.objects.filter(
            user_id=request.user.id)

        favorite_articles = []
        for favorite in favorites_queryset:
            article = TheArticleSerializer(favorite.article_id).data
            favorite_articles.append(article)
        favorites = {
            "favorites": favorite_articles
        }
        return Response(data=favorites, status=status.HTTP_200_OK)


class RatingView(APIView):
    """This class handles post and put requests of an article rating."""
    serializer_class = RatingSerializer()
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug):
        data = request.data.get('rating')
        value = data['value']
        review = data['review']

        try:
            article = self.serializer_class.get_article(slug)
            count = Rating.objects.filter(article=article,
                                          user=request.user.id).count()
            if count > 0:
                return Response({"message":
                                 "You have already rated this article."},
                                status=status.HTTP_403_FORBIDDEN)

            user_id = article.author_id
            article_id = article.id

            if user_id == request.user.id:

                return Response({"message":
                                "You cannot rate your own article."},
                                status=status.HTTP_403_FORBIDDEN
                                )
            else:
                data = {
                    "user": request.user.id,
                    "article": article_id,
                    "value": value,
                    "review": review
                }

            serializer = RatingSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message":
                            "Article rated."},
                            status=status.HTTP_201_CREATED)

        except Article.DoesNotExist:
            return Response({"message": "This article was not found."},
                            status=status.HTTP_404_NOT_FOUND)

    def put(self, request, slug):
        try:
            article = self.serializer_class.get_article(slug)
            rating = Rating.objects.get(
                article=article.id, user=request.user.id)
            data = request.data.get('rating')

            serializer = RatingSerializer(
                instance=rating, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Rating updated."})

        except Article.DoesNotExist:
            return Response({"message": "This article was not found."},
                            status=status.HTTP_404_NOT_FOUND)
        except Rating.DoesNotExist:
            return Response({"message": "You have not rated this article."},
                            status=status.HTTP_404_NOT_FOUND)


class GetRatingView(APIView):
    """This class handles get requests of an article rating."""
    pagination_class = LimitOffsetPagination
    serializer_class = RatingSerializer()
    permission_classes = (AllowAny,)

    def get(self, request, slug):
        try:
            article = self.serializer_class.get_article(slug)
            rating_queryset = Rating.objects.filter(article=article)
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(rating_queryset, request)
            serializer = ArticleRatingSerializer(page,
                                                 many=True,
                                                 context={"current_user":
                                                          request.user}, )

            count = Rating.objects.filter(article=article.id).\
                exclude(review__exact='').count()
            if count > 0:
                return paginator.get_paginated_response(serializer.data)

            return Response({
                "message": "This article has no reviews."
            },
                status=status.HTTP_404_NOT_FOUND
            )

        except Article.DoesNotExist:
            return Response({
                "message": "This article was not found."
            },
                status=status.HTTP_404_NOT_FOUND
            )
