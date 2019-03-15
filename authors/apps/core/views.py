from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class BaseManageView(APIView):
    """
    The base class for ManageViews
        A ManageView is a view which i
        s used to dispatch the requests to the appropriate views
        This is done so that we can use one URL with different
         methods (GET, PUT, etc)
    """

    def dispatch(self, request, *args, **kwargs):
        if request.method not in self.VIEWS_BY_METHOD.keys():
            return MethodNotAllowedView.as_view()(request, *args, **kwargs)
        return self.VIEWS_BY_METHOD[request.
                                    method]()(request, *args, **kwargs)


class MethodNotAllowedView(APIView):
    """Handles Unused methods"""

    def action(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
