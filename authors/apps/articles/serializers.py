from rest_framework import serializers

from authors.apps.profiles.serializers import ProfileSerializer

from .models import (Article, CommentLike, Favorite, Like, Snapshot,
                     ThreadedComment)


class TheArticleSerializer(serializers.ModelSerializer):

    reading_time = serializers.ReadOnlyField(source='get_reading_time')

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'body', 'draft', 'slug', 'reading_time',
            'editing', 'description', 'published', 'activated',
            "created_at", "updated_at", 'author'
        ]
        read_only_fields = ['slug']

    def create(self, validated_data):
        '''Create a new Article instance, given the accepted data.'''
        article = Article.objects.create(**validated_data)
        return article

    def update(self, instance, validated_data):
        '''Enable update on articles already existing and returns it.'''

        instance.title = validated_data.get(
            'title', instance.title
        )
        instance.body = validated_data.get('body', instance.body)
        instance.draft = validated_data.get(
            'draft', instance.draft
        )
        instance.editing = validated_data.get('editing', instance.editing)
        instance.description = validated_data.get(
            'description', instance.description
        )
        instance.published = validated_data.get(
            'published', instance.published
        )
        instance.activated = validated_data.get(
            'activated', instance.activated
        )
        instance.save()
        return instance


class LikesSerializer(serializers.ModelSerializer):
    """
    Serializers for likes
    """
    class Meta():
        model = Like
        fields = ('id', 'user_id', 'article_id', 'is_like')
        read_only_fields = ['id']


class ArticleCommentInputSerializer(serializers.ModelSerializer):
    """Seriliazes input data and creates a new article comment."""
    class Meta:
        model = ThreadedComment
        fields = ('article', 'author', 'body')
        extra_kwargs = {'article': {'required': True}}


class CommentCommentInputSerializer(serializers.ModelSerializer):
    """Serializes input data and creates a new comment comment."""
    class Meta:
        model = ThreadedComment
        fields = ('article', 'comment', 'author', 'body')
        extra_kwargs = {'comment': {'required': True}}


class SnapshotSerializer(serializers.ModelSerializer):
    """Serializer for displaying comment snapshots."""
    class Meta:
        model = Snapshot
        fields = ('id', 'body', 'timestamp')


class CommentSerializerMixin(serializers.ModelSerializer):
    """Adds the is_liked serializer method field."""
    is_liked = serializers.SerializerMethodField()
    likes = serializers.Field(source='total_likes')

    def get_is_liked(self, obj):
        current_user = self.context.get('current_user', None)
        return obj.likes.filter(user__id__in=[current_user.id]).exists()


class EmbededCommentOutputSerializer(CommentSerializerMixin):
    """Seriliazes comment and gives output data."""
    author = ProfileSerializer()
    edit_history = SnapshotSerializer(many=True, source='snapshots')

    class Meta:
        model = ThreadedComment
        fields = ('id', 'created_at', 'updated_at', 'edited', 'is_liked',
                  'total_likes', 'body', 'author', 'edit_history')


class ThreadedCommentOutputSerializer(CommentSerializerMixin):
    """Seriliazes comment and gives output data."""
    author = ProfileSerializer()
    comments = EmbededCommentOutputSerializer(many=True)
    edit_history = SnapshotSerializer(many=True, source='snapshots')

    class Meta:
        model = ThreadedComment
        fields = ('id', 'created_at', 'updated_at', 'edited', 'is_liked',
                  'total_likes', 'body', 'author', 'edit_history', 'comments')


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Serializers for favorites
    """
    class Meta():
        model = Favorite
        fields = ('id', 'user_id', 'article_id')
        read_only_fields = ['id']


class CommentLikeSerializer(serializers.ModelSerializer):
    """Serializes comment_like input."""
    class Meta:
        model = CommentLike
        fields = ('id', 'user', 'comment')
        read_only_fields = ('id',)
