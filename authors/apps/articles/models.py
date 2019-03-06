from django.conf import settings
from django.db import models
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

    class Meta:
        ordering = ["-created_at", "-updated_at"]



