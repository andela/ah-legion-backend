from rest_framework import serializers
from .models import Profile
from ..authentication.models import User


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


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('app_notifications', 'email_notifications')


    def update_permissions(self, user=None, data=None):
        
        user.profile.app_notifications['user-follow'] = data['app_notifications_permissions']['user-follow']
        user.profile.app_notifications['article-liked'] = data['app_notifications_permissions']['article-liked']
        user.profile.app_notifications['article-commented'] = data['app_notifications_permissions']['article-commented']
        user.profile.app_notifications['article-published'] = data['app_notifications_permissions']['article-published']
        user.profile.app_notifications['comment-commented'] = data['app_notifications_permissions']['comment-commented']
        user.profile.app_notifications['article-favourited'] = data['app_notifications_permissions']['article-favourited']

        user.profile.email_notifications['user-follow'] = data['email_notifications_permissions']['user-follow']
        user.profile.email_notifications['article-liked'] = data['email_notifications_permissions']['article-liked']
        user.profile.email_notifications['article-commented'] = data['email_notifications_permissions']['article-commented']
        user.profile.email_notifications['article-published'] = data['email_notifications_permissions']['article-published']
        user.profile.email_notifications['comment-commented'] = data['email_notifications_permissions']['comment-commented']
        user.profile.email_notifications['article-favourited'] = data['email_notifications_permissions']['article-favourited']

        user.profile.save()

        return {"app_notifications_permissions":user.profile.app_notifications, "email_notifications_permissions":user.profile.email_notifications}