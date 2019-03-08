from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import Profile
from .renderers import ProfileJSONRenderer
from .serializers import ProfileSerializer
from .exceptions import ProfileDoesNotExist


class ProfileRetrieveAPIView(RetrieveAPIView):
    """
    Class endpoint for retreving a single user profile
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    @swagger_auto_schema(query_serializer=serializer_class,
                         responses={201: serializer_class()})
    def get(self, request, username, *args, **kwargs):
        """ function to retrieve a requested profile """
        try:
            profile = Profile.objects.select_related('user').get(
                user__username=username
            )
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        serializer = self.serializer_class(profile)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileListApiView(ListAPIView):
    """
    Class endpoint for retreving a single user profile
    """
    queryset = Profile.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
