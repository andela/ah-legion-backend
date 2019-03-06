from rest_framework import (
    generics, mixins, status
)

from rest_framework.permissions import (
    AllowAny, IsAuthenticated,
)
from rest_framework.response import Response
from .renderers import ArticleJSONRenderer
from .serializers import TheArticleSerializer
from .models import Article


# Create your views here.
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
        # Decode token
        this_user = request.user
        payload['author'] = this_user.pk

        serializer = TheArticleSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetArticlesView(
    mixins.ListModelMixin, generics.GenericAPIView
):
    queryset = Article.objects.all()
    permission_classes = (AllowAny,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = (TheArticleSerializer)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        # Decode token
        reply_not_found = {}
        reply_found = []
        published_articles = Article.objects.filter(
            published=True, activated=True)

        if (len(published_articles) < 1):
            reply_not_found["detail"] = "No articles have been found."
            return Response(
                reply_not_found,
                status=status.HTTP_404_NOT_FOUND
            )

        for item in published_articles:
            serialized = self.serializer_class(item)
            reply_found.append(serialized.data)

        return Response(
            reply_found,
            status=status.HTTP_200_OK
        )


class GetAnArticleView(
    mixins.RetrieveModelMixin, generics.GenericAPIView
):
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


class UpdateAnArticleView(
    mixins.UpdateModelMixin, generics.GenericAPIView
):
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
            serialized = self.serializer_class(
                article_obj, data=the_data, partial=True
            )
            serialized.is_valid(raise_exception=True)
            self.perform_update(serialized)
            if "activated" in the_data.keys()\
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
