from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    serializers for user profile upon user registration.
    """

    username = serializers.ReadOnlyField(source='get_username')
    image_url = serializers.ReadOnlyField(source='get_cloudinary_url')
    following = serializers.SerializerMethodField()

    class Meta:
        model = Profile

        fields = (
            'username', 'first_name', 'last_name', 'bio', 'image', 'image_url',
            'website', 'city', 'phone', 'country', 'following')

        read_only_fields = ("created_at", "updated_at")

    def get_following(self, obj):
        current_user = self.context.get('current_user', None)
        following = Profile.objects.filter(
            pk=current_user.pk, followings=obj.pk).exists()
        return following


class MultipleProfileSerializer(serializers.ModelSerializer):
    """
    serializers for user profile upon user registration.
    """

    username = serializers.ReadOnlyField(source='get_username')
    image_url = serializers.ReadOnlyField(source='get_cloudinary_url')

    class Meta:
        model = Profile

        fields = (
            'username', 'first_name', 'last_name', 'bio', 'image_url',
            'website', 'city', 'phone', 'country')

        read_only_fields = ("created_at", "updated_at")


class FollowUnfollowSerializer(serializers.ModelSerializer):
    """Serializer that returns id, username, followers, following"""

    followers_total = serializers.SerializerMethodField()
    following_total = serializers.SerializerMethodField()
    username = serializers.ReadOnlyField(source='get_username')

    class Meta:
        model = Profile
        fields = (
            'id', 'username', 'followers_total', 'following_total',
        )

    def get_followers_total(self, obj):
        """Returns number of users one is following"""
        return obj.followers.count()

    def get_following_total(self, obj):
        """Returns total number of followers"""
        return obj.followings.count()


class FollowerFollowingSerializer(serializers.ModelSerializer):
    """Serializer that return username"""
    username = serializers.ReadOnlyField(source='get_username')
    following = serializers.SerializerMethodField()
    image_url = serializers.ReadOnlyField(source='get_cloudinary_url')

    class Meta:
        model = Profile
        fields = (
            'username', 'first_name',
            'last_name', 'bio', 'image_url',
            'city', 'website', 'phone',
            'country', 'following')

    def get_following(self, obj):
        current_user = self.context.get('current_user', None)
        following = Profile.objects.filter(
            pk=current_user.pk, followings=obj.pk).exists()
        return following
