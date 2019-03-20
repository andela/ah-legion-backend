import readtime

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from authors.apps.core.abstract_models import TimeStamped
from authors.apps.profiles.models import Profile

from . import managers
from .utils import generate_unique_slug


class Article(models.Model):
    """This model implements storage of every article within authors heaven."""
    title = models.CharField(max_length=150, db_index=True, blank=False)
    slug = models.SlugField(max_length=170, db_index=True, unique=True)
    body = models.TextField(blank=False, null=False)
    draft = models.TextField(blank=True, null=True)
    # [editing]True if user is currently editing the article
    editing = models.BooleanField(default=False)
    description = models.CharField(max_length=255, null=True)
    published = models.BooleanField(default=False)
    activated = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    objects = models.Manager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        '''Saves all the changes of model article'''
        if not self.slug:
            self.slug = generate_unique_slug(self, "title", "slug")

        update_slug = generate_unique_slug(self, "title", "slug")
        art = Article.objects.filter(slug=self.slug).first()
        if art and art.title != self.title:
            self.slug = update_slug

        super().save(*args, **kwargs)

    def get_reading_time(self):
        result = readtime.of_text(str(self.body))
        reading_time = result.minutes
        unit = " minutes"

        return str(reading_time) + unit

    class Meta:
        ordering = ["-created_at", "-updated_at"]


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
