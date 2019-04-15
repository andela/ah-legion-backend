from django.utils.text import slugify
from rest_framework.response import Response
from rest_framework import status


def generate_unique_slug(model_instance, slugable_field_name, slug_field_name):
    """
    Takes a model instance, sluggable field name (such as 'title') of that
    model as string, slug field name (such as 'slug') of the model as string
    returns a unique slug as a string.
    """
    slug = slugify(getattr(model_instance, slugable_field_name))
    unique_slug = slug
    extension = 1
    ModelClass = model_instance.__class__

    while ModelClass._default_manager.filter(
        **{slug_field_name: unique_slug}
    ).exists():
        unique_slug = '{}-{}'.format(slug, extension)
        extension += 1

    return unique_slug


def edit_article(instance, request, the_data, tag_instance=None):
    if instance.get_object().author.user.username == request.user.username:
        if instance.get_object().activated is False:
            invalid_entry = {
                "detail": "This article does not exist."
            }
            return Response(
                invalid_entry,
                status=status.HTTP_404_NOT_FOUND
            )

        article_obj = instance.get_object()
        serialized = instance.serializer_class(
            article_obj, data=the_data, partial=True,
            context={"current_user": request.user, "request": request}
        )
        serialized.is_valid(raise_exception=True)
        instance.perform_update(serialized)
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
