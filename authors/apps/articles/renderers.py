import json

from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

from ..articles.models import Tag


class ArticleJSONRenderer(JSONRenderer):
    '''JSONRenderClass for formatting Article model data into JSON.'''
    charset = 'utf-8'

    def _single_article_formatting(self, data):
        tags = data.pop("tags")
        tagList = []
        for item in tags:
            this_tag = Tag.objects.filter(pk=item).first()
            tagList.append(this_tag.tag)
        data["tagList"] = tagList
        return data

    def render(self, data, media_type=None, renderer_context=None):
        """Return data in json format."""
        if type(data) == ReturnDict:
            # single article
            my_data = self._single_article_formatting(data)
            return json.dumps({
                'Article': my_data
            })
        elif type(data) is ReturnList:
            return json.dumps({
                'Articles': data
            })
        else:
            # many articles
            if "results" in data.keys():
                for item in data["results"]:
                    item = self._single_article_formatting(item)
            return json.dumps({
                'Articles': data
            })


class CommentJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):

        if type(data) == ReturnDict:
            return json.dumps({'Comment': data})

        return json.dumps({'Comments': data})


class ReportJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):

        # Finally, we can render our data under the "profile" namespace.
        return json.dumps({
            'report_details': data

        })


class SearchJSONRenderer(JSONRenderer):
    '''Returns results from a search of articles'''
    charset = 'utf-8'
    article_formatting = ArticleJSONRenderer()

    def render(self, data, media_type=None, renderer_context=None):
        if "results" in data.keys():
            for item in data["results"]:
                item = self.article_formatting._single_article_formatting(item)
        return json.dumps(data)
