from django.db.models import QuerySet


class CommentQuerySet(QuerySet):
    """Custom querysets for for the Comment model."""

    def _active(self):
        """Return only active comments."""
        return self.filter(is_active=True)

    def all_comments(self):
        """Return all active comments."""
        return self._active()

    def for_author(self, author_profile):
        """Return active comments for a given author."""
        return self._active().filter(author=author_profile)

    def for_article(self, article):
        """Return active comments for a given article."""
        return self._active().filter(article=article)

    def for_comment(self, comment):
        """Return active comments for a given article."""
        return self._active().filter(comment=comment)
