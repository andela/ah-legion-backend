from authors.apps.profiles.serializers import ProfileSerializer
from authors.apps.profiles.models import Profile
from .models import (Article, Favorite, Like, Snapshot,
                     ThreadedComment, Rating, Tag, Bookmark)
from rest_framework import serializers


class TheArticleSerializer(serializers.ModelSerializer):

    reading_time = serializers.ReadOnlyField(source='get_reading_time')
    average_rating = serializers.ReadOnlyField(source='get_average_rating')
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'body', 'draft', 'slug',
            'reading_time', 'average_rating', 'tags',
            'editing', 'description', 'published', 'activated',
            "created_at", "updated_at", 'author'
        ]
        read_only_fields = ['slug']

    def create(self, validated_data):
        '''Create a new Article instance, given the accepted data.'''
        article_data = validated_data
        tags_data = None
        if 'tags' in validated_data.keys():
            tags_data = article_data.pop("tags")

        current_user = self.context.get('current_user', None)
        user_profile = Profile.objects.filter(user=current_user).first()
        article_data["author"] = user_profile
        article = Article.objects.create(**article_data)
        if tags_data:
            for item in tags_data:
                my_tag = Tag()
                found = my_tag._create_tag(item)
                article.tags.add(found)
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
        if 'tags' in validated_data.keys() and len(validated_data['tags']) > 0:
            this_tag = Tag()
            new_tags = validated_data['tags']
            this_tag._update_article_tags(instance, new_tags)

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


class EmbededCommentOutputSerializer(serializers.ModelSerializer):
    """Seriliazes comment and gives output data."""
    author = ProfileSerializer()
    edit_history = SnapshotSerializer(many=True, source='snapshots')

    class Meta:
        model = ThreadedComment
        fields = ('id', 'created_at', 'updated_at', 'edited', 'body', 'author',
                  'edit_history')


class ThreadedCommentOutputSerializer(serializers.ModelSerializer):
    """Seriliazes comment and gives output data."""
    author = ProfileSerializer()
    comments = EmbededCommentOutputSerializer(many=True)
    edit_history = SnapshotSerializer(many=True, source='snapshots')

    class Meta:
        model = ThreadedComment
        fields = ('id', 'created_at', 'updated_at', 'edited', 'body', 'author',
                  'edit_history', 'comments')


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Serializers for favorites
    """
    class Meta():
        model = Favorite
        fields = ('id', 'user_id', 'article_id')
        read_only_fields = ['id']


class RatingSerializer(serializers.ModelSerializer):
    """Handles serialization of article ratings."""
    value = serializers.IntegerField(
        min_value=1,
        max_value=5,
        required=True)

    class Meta:
        model = Rating
        fields = ['user', 'article', 'value', 'review']

    def get_article(self, slug):
        article = Article.objects.get(slug=slug, published=True, activated=True)
        return article


class ArticleRatingSerializer(serializers.ModelSerializer):
    """Handles deserialization of article ratings."""
    image = serializers.ReadOnlyField(source='get_image')
    username = serializers.ReadOnlyField(source='get_username')
    user = {"username": username, "image": image}

    class Meta:
        model = Rating
        fields = ['value', 'review', 'username', 'image']


class BookmarkSerializer(serializers.ModelSerializer):
    """
    Serializers for bookmarks
    """
    class Meta():
        model = Bookmark
        fields = ('id', 'user_id', 'article_id')
        read_only_fields = ['id']


class PersonalArticlesSerializer(serializers.ModelSerializer):
    """
    separate serilizer for getting all
    articles belonging to logged in user
    no need of 'author' field since
    they all belong to the currently logged in user.
    """

    reading_time = serializers.ReadOnlyField(source='get_reading_time')
    average_rating = serializers.ReadOnlyField(source='get_average_rating')

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'body', 'draft', 'slug',
            'reading_time', 'average_rating', 'tags',
            'editing', 'description', 'published', 'activated',
            "created_at", "updated_at"
        ]
        read_only_fields = ['slug']
