from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User
from authors.apps.profiles.serializers import ProfileSerializer


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    # Ensure passwords are at least 8 characters long, no longer than 128
    # characters, and can not be read by the client.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        required=True,
        validators=[RegexValidator(
            regex='^[a-zA-Z0-9]*$',
            message='Password should be alphanumeric',
            code='invalid_password')],
        error_messages={
            'min_length': 'Password should be at least 8 characters long',
            'max_length': 'Password should not be longer than 128 characters',
            'blank': 'Password field cannot be blank',
            'required': 'Password is required'

        }
    )

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        fields = ['email', 'username', 'password']
        extra_kwargs = {
            'email': {
                'error_messages': {
                    'required': 'Email is required',
                    'blank': 'Email field cannot be blank',
                    'invalid': 'Please enter a valid email address'
                },
                'validators': [
                    UniqueValidator(queryset=User.objects.all(),
                                    message='A user with this '
                                            'email already exists')]

            },
            'username': {
                'error_messages': {
                    'required': 'Username is required',
                    'blank': 'Username field cannot be blank'},
                'validators': [
                    UniqueValidator(queryset=User.objects.all(),
                                    message='A user with this '
                                            'username already exists')]

            }

        }

    def create(self, validated_data):
        # Use the `create_user` method we wrote earlier to create a new user.
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        email = data.get('email', None)
        password = data.get('password', None)

        # As mentioned above, an email is required. Raise an exception if an
        # email is not provided.
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        # As mentioned above, a password is required. Raise an exception if a
        # password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` value. Remember that, in our User
        # model, we set `USERNAME_FIELD` as `email`.
        user = authenticate(username=email, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag to tell us whether the user has been banned
        # or otherwise deactivated. This will almost never be the case, but
        # it is worth checking for. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            'email': user.email,
            'username': user.username,
            'token': user.token
        }


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128
    # characters. These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so let's just stick with the defaults.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'token', 'profile',)
        read_only_fields = ('token',)

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        password = validated_data.pop('password', None)
        profile_data = validated_data.pop('profile', {})

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)

        instance.save()

        for (key, value) in profile_data.items():
            setattr(instance.profile, key, value)

        # Save profile
        instance.profile.save()

        return instance
