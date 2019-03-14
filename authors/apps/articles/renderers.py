import json
from cloudinary import CloudinaryImage
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnDict
from ..authentication.models import User


class ArticleJSONRenderer(JSONRenderer):
    '''JSONRenderClass for formatting Article model data into JSON.'''
    charset = 'utf-8'

    def _single_article_formatting(self, data):
        author = User.objects.all().filter(
            pk=data['author']).first()
        the_data = {
            "username": author.username,
            "bio": "None",
            "image": "None"
        }
        profile = author.profile
        if profile:
            the_data["bio"] = profile.bio
            img = str(author.profile.image)
            image_url = CloudinaryImage(img).build_url(
                width=100, height=150, crop='fill'
            )
            the_data["image"] = image_url
        data['author'] = the_data
        return data

    def render(self, data, media_type=None, renderer_context=None):
        """Return data in json format."""
        if type(data) == ReturnDict:
            # single article
            try:
                my_data = self._single_article_formatting(data)
                return json.dumps({
                    'Article': my_data
                })
            except (KeyError, TypeError, ValueError):
                return json.dumps({
                    'Article': data
                })
        else:
            # many articles
            try:
                reply = []
                the_articles = data['results']
                for item in the_articles:
                    my_data = self._single_article_formatting(item)
                    reply.append(my_data)

                data['results'] = reply
                return json.dumps({
                    'Articles': data
                })
            except (KeyError, TypeError, ValueError):
                return json.dumps({
                    'Article': data
                })

