from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Snapshot, ThreadedComment


@receiver(post_save, sender=ThreadedComment)
def take_comment_snapshot_handler(sender, instance, created, **kwargs):
    """Make a snapshot of a comment body everytime the comment is edited
    except for when it has just been newly created.
    """
    if created:
        return
    snapshot = Snapshot.objects.create(comment=instance, body=instance.body,
                                       highlight=instance.highlight)
    snapshot.save()
