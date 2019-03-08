import json

from rest_framework.renderers import JSONRenderer


class UserJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        # If the view throws an error (such as the user can't be authenticated
        # or something similar), `data` will contain an `errors` key. We want
        # the default JSONRenderer to handle rendering errors, so we need to
        # check for this case.
        errors = data.get('errors', None)

        if errors is not None:
            # As mentioned about, we will let the default JSONRenderer handle
            # rendering errors.
            return super().render(data)

        # Finally, we can render our data under the "user" namespace.
        image_prefix = "https://res.cloudinary.com/dbsri2qtr/"
        try:
            image_suffix = data['profile']['image']
            data['profile']['image'] = image_prefix + image_suffix

        except KeyError:
            pass
        return json.dumps({
            'user': data
        })
