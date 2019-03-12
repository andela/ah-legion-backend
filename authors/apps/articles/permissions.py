from rest_framework import permissions

from .models import ThreadedComment


class CanCreateComment(permissions.BasePermission):
    """For read only operations allow, for write perissions make sure they
    are authenticated.
    """
    message = "User cannot create comment unless they are authenticated."

    def has_permission(self, request, view):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return user.is_authenticated


class CanEditComment(permissions.BasePermission):
    """For Read only operations allow, for write operations check
    whether the user is authenticated and owns the comment.
    """

    message = "User is not authorized to edit this comment."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        elif isinstance(obj, ThreadedComment) and user.is_authenticated:
            return obj.author == user.profile

        return False
