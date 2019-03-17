import json
from rest_framework.renderers import JSONRenderer


class NotificationRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None, **kwargs):

        return json.dumps({
            'notifications': data
        })
