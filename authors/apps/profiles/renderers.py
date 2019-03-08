import json

from rest_framework.renderers import JSONRenderer


class ProfileJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        """
        Check for errors key in data
        """
        errors = data.get('errors', None)

        if errors:
            """
            We will let the default JSONRenderer handle
            rendering errors.
            """
            return super(ProfileJSONRenderer, self).render(data)

        # Finally, we can render our data under the "profile" namespace.
        image_prefix = "https://res.cloudinary.com/dbsri2qtr"
        try:
            image_suffix = data['image']
            data['image'] = image_prefix + image_suffix

        except KeyError:
            pass

        return json.dumps({
            'profile': data
        })
