from django.conf import settings
from django.contrib.postgres.fields import HStoreField
from django.db import models
from django.db.models.signals import post_save
from authors.apps.core.models import TimeStampModel
from cloudinary.models import CloudinaryField
from cloudinary import CloudinaryImage
from authors.apps.notifications.backends import get_default_permissions


class Profile(TimeStampModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(
        'first name', max_length=30, blank=True, null=True)
    last_name = models.CharField(
        'last name', max_length=30, blank=True, null=True)
    birth_date = models.DateField('last name', null=True, blank=True)
    bio = models.TextField('bio', default='', null=True, blank=True)
    city = models.CharField('city', blank=True, null=True,
                            max_length=100, default='')
    country = models.CharField('country', blank=True,
                               null=True, max_length=100, default='')
    phone = models.IntegerField('phone', blank=True, null=True, default=0)
    website = models.URLField('website', blank=True, null=True, default='')
    image = CloudinaryField(
        'image', default="image/upload/v1552193974/gyzbaptikqalgthxfdnh.png")  # noqa
    followings = models.ManyToManyField(
        'self', related_name='followers', symmetrical=False)
    app_notifications = HStoreField(default=get_default_permissions)
    email_notifications = HStoreField(default=get_default_permissions)

    def __str__(self):
        return self.user.username

    @property
    def get_username(self):
        return self.user.username

    def get_cloudinary_url(self):
        image_url = CloudinaryImage(str(self.image)).build_url(
            width=100, height=150, crop='fill')
        return image_url


"""
Signal receiver for 'post_save' signal sent by User model upon saving
"""


def create_profile(sender, **kwargs):
    if kwargs.get('created'):
        user_profile = Profile(user=kwargs.get('instance'))
        user_profile.save()


# connect the signal to the handler function
post_save.connect(create_profile, sender=settings.AUTH_USER_MODEL)

