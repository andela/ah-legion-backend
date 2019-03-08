from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema

from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend
from social_core.backends.oauth import BaseOAuth1

from .renderers import UserJSONRenderer
from .serializers import (LoginSerializer, RegistrationSerializer,
                          UserSerializer, SocialAuthenticationSerializer)
from .utils import validate_image


class RegistrationAPIView(APIView):
    """
    post:
        Register a new user by creating a new user instance.
    """
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    @swagger_auto_schema(query_serializer=RegistrationSerializer,
                         responses={201: UserSerializer()})
    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    """
    post:
        Login an exising user
    """
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    @swagger_auto_schema(query_serializer=LoginSerializer,
                         responses={200: UserSerializer()})
    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    get:
        Retrieve details of a user

    put:
        Update all details of a user

    patch:
        Update a single detail of a user
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        image = self.request.data.get('image')

        validate_image(image)

        serializer_data = request.data
        user_data = {
            'username': serializer_data.get('username', request.user.username),
            'email': serializer_data.get('email', request.user.email),
            'profile': {
                'first_name': serializer_data.get(
                    'first_name', request.user.profile.last_name),
                'last_name': serializer_data.get(
                    'last_name', request.user.profile.last_name),
                'birth_date': serializer_data.get(
                    'birth_date', request.user.profile.birth_date),
                'bio': serializer_data.get('bio', request.user.profile.bio),
                'image': serializer_data.get(
                    'image', request.user.profile.image),
                'city': serializer_data.get(
                    'city', request.user.profile.city),
                'country': serializer_data.get(
                    'country', request.user.profile.country),
                'phone': serializer_data.get(
                    'phone', request.user.profile.phone),
                'website': serializer_data.get(
                    'website', request.user.profile.website),

            }
        }

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=user_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class SocialAuthenticationView(CreateAPIView):
    """
    Login to the site via social authentication
     services (Google, Twitter, Facebook)
    """
    permission_classes = (AllowAny,)
    serializer_class = SocialAuthenticationSerializer
    renderer_classes = (UserJSONRenderer,)

    def create(self, request):
        """Creates user if not present and returns an authentication token"""
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        provider = serializer.data.get("provider")
        authenticated_user = request.user if not \
            request.user.is_anonymous else None
        strategy = load_strategy(request)

        # Load backend associated with the provider
        try:

            backend = load_backend(
                strategy=strategy, name=provider, redirect_uri=None)

            access_token = serializer.data.get("access_token")
            if isinstance(backend, BaseOAuth1):
                access_token = {
                    'oauth_token': request.data['access_token'],
                    'oauth_token_secret': request.data['access_token_secret']
                }

        except MissingBackend:
            error_msg = """Provider not supported, Please use 'google-oauth2',
             'facebook', or 'twitter'."""
            return Response({"error": error_msg},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = backend.do_auth(access_token, user=authenticated_user)

        except BaseException as error:
            return Response({"error": str(error)},
                            status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.save()
        serializer = UserSerializer(user)
        serializer.instance = user
        return Response(serializer.data, status=status.HTTP_200_OK)
