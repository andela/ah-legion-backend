import readtime

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from authors.apps.core.abstract_models import TimeStamped
from authors.apps.profiles.models import Profile

from . import managers
from .utils import generate_unique_slug
from cloudinary import CloudinaryImage
from django.utils.text import slugify


class Article(models.Model):
    """This model implements storage of every article within authors heaven."""
    title = models.CharField(max_length=150, db_index=True, blank=False)
    slug = models.SlugField(max_length=170, db_index=True, unique=True)
    body = models.TextField(blank=False, null=False)
    draft = models.TextField(blank=True, null=True)
    editing = models.BooleanField(default=False)
    description = models.CharField(max_length=255, null=True)
    published = models.BooleanField(default=False)
    activated = models.BooleanField(default=True)
    tags = models.ManyToManyField('Tag', related_name='articles', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        Profile, related_name="articles",
        on_delete=models.CASCADE
    )

    objects = models.Manager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        '''Saves all the changes of model article'''
        if not self.slug:
            self.slug = generate_unique_slug(self, "title", "slug")
        super().save(*args, **kwargs)

    def get_reading_time(self):
        result = readtime.of_text(str(self.body))
        reading_time = result.minutes
        unit = " minutes"

        return str(reading_time) + unit


class Like(models.Model):
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='likes')
    article_id = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='likes')
    is_like = models.BooleanField()


class ThreadedComment(TimeStamped):
    """Comment model for articles and other comments."""
    author = models.ForeignKey(Profile, related_name='article_comments',
                               on_delete=models.CASCADE)
    article = models.ForeignKey('Article', related_name='comments',
                                on_delete=models.CASCADE)
    comment = models.ForeignKey('self', related_name='comments', null=True,
                                on_delete=models.CASCADE)
    body = models.TextField(_("Body"))
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = managers.CommentQuerySet.as_manager()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.author}: {self.body:10}...'

    def soft_delete(self):
        """Make a soft deletion by changing the is_active field."""
        self.is_active = False
        self.save()

    def undo_soft_deletion(self):
        """Undo a soft deleteion."""
        self.is_active = True
        self.save()

    def for_comment(self):
        """Check whether this comment is for another comment."""
        if self.comment:
            return True
        return False

    @cached_property
    def edited(self):
        """Return whether the comment has been edited."""
        return self.snapshots.all().exists()


class Snapshot(models.Model):
    """Model to take snapshots of comments everytime they are edited."""
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey('ThreadedComment', related_name='snapshots',
                                on_delete=models.CASCADE)
    body = models.TextField(_("Body"))

    class Meta:
        ordering = ('-timestamp',)
        verbose_name = _("Comment Snapshot")
        verbose_name_plural = _("Comment Snapshots")


class Favorite(models.Model):
    """Implement storage of favorites"""
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='favorites')
    article_id = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='favorites')


class Rating(models.Model):
    """This class creates an article rating model."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='ratings',
        on_delete=models.CASCADE
    )
    article = models.ForeignKey(
        Article,
        related_name='ratings',
        on_delete=models.CASCADE
    )
    value = models.IntegerField(null=False)
    review = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now=True)

    def get_username(self):
        """This method gets the username of the user rating an article."""
        return self.user.username

    def get_image(self):
        """This method gets the image of the user rating an article."""
        image_url = CloudinaryImage(str(self.user.profile.image)).build_url(
            width=100, height=150, crop='fill')
        return image_url

    def __str__(self):
        return "This is rating no: " + str(self.id)


class Tag(models.Model):
    tag = models.CharField(max_length=100, db_index=True, unique=True)
    slug = models.SlugField(max_length=240, db_index=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.tag)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.slug

    objects = models.Manager()

    def _create_tag(self, tag_name):
        '''
        This method checks if the tag exists and returns the tag object
        else it creates a new tag object and returns it.
        '''
        found = Tag.objects.filter(slug=slugify(tag_name))
        if len(found) < 1:
            Tag.objects.create(tag=tag_name)
        return Tag.objects.filter(slug=slugify(tag_name)).first()

    def _remove_tags_without_articles(self, tag_name):
        '''This method takes a tag name and checks if the tag has
        associated articles and if not it deletes the tag from the
        database in order to save on database space.
        '''
        found = Tag.objects.filter(slug=slugify(tag_name))
        if found and len(found) > 0:
            the_tag = Tag.objects.filter(slug=slugify(tag_name)).first()
            its_articles = the_tag.articles.all()
            if len(its_articles) < 1:
                the_tag.delete()
                return True
        return False

    def _update_article_tags(self, instance, new_tag_list):
        '''This method is used to update the tags of an
        article and do general tag mainenance.'''
        old_tags = instance.tags.all()
        old_tag_slugs = [tag.slug for tag in old_tags]
        new_tag_slugs = [slugify(tag) for tag in new_tag_list]
        # Check for items in the old list that are not in the new
        # list and remove them.
        tags_to_remove = list(set(old_tag_slugs) - set(new_tag_slugs))
        remove_tag_objects = [
            tag for tag in old_tags if (
                tag.slug in tags_to_remove
            )
        ]
        for item in remove_tag_objects:
            # Remove tag from article
            instance.tags.remove(item)
            # Check if tag has any other article else delete the tag.
            self._remove_tags_without_articles(item.tag)
        new_slugs = list(set(new_tag_slugs) - set(old_tag_slugs))
        tags_to_add = [tag for tag in new_tag_list if(
            slugify(tag) in new_slugs
        )]
        for item in tags_to_add:
            # Create tag if tag does not exist
            the_tag = self._create_tag(item)
            # Add the tag to the article instance.
            instance.tags.add(the_tag)
        return True


class Bookmark(models.Model):
    """Stores article bookmarks"""
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bookmarks')
    article_id = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='bookmarks')

    class Meta:
        verbose_name = _("Article bookmark")
        verbose_name_plural = _("Article bookmarks")
