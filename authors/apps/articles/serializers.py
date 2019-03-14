from rest_framework import serializers
from .models import Article


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

