from django.db import models


class TimeStamped(models.Model):
    """
    Provides timstamp fields of created and updated.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
