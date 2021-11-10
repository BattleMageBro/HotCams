from functools import partial

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.db import models
from taggit.managers import TaggableManager


make_stream_key = partial(get_random_string, 20)

User = get_user_model()


class Preview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='recipes')
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    description = models.TextField()
    pub_date = models.DateTimeField('date_published', auto_now_add=True,
                                    db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Preview'
        verbose_name_plural = 'Previews'
        ordering = ['-pub_date']


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)


class Stream(models.Model):

    user = models.OneToOneField(
        User, related_name="stream", on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='images/streams', blank=True, null=True)
    key = models.CharField(max_length=20, default=make_stream_key, unique=True)
    started_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    @property
    def is_live(self):
        return self.started_at is not None

    @property
    def hls_url(self):
        return reverse("hls-url", args=(self.key,))

@receiver(post_save, sender=User, dispatch_uid="create_stream_for_user")
def create_stream_for_user(sender, instance=None, created=False, **kwargs):
    """ Create a stream for new users.
    """
    if created:
        Stream.objects.create(user=instance)

