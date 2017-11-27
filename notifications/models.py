from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from users.models import User, Email


class NotificationType(models.Model):
    entity = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    description = models.TextField()
    subject = models.CharField(max_length=75)
    template_name = models.CharField(max_length=100)

    def __str__(self):
        return ";".join([self.entity, self.name])


class Notification(models.Model):
    user = models.ForeignKey(User, blank=False, related_name='notifications')
    read = models.BooleanField(default=False)

    # Who/what did it
    actor_content_type = models.ForeignKey(ContentType, related_name='notify_actor')
    actor_object_id = models.UUIDField()
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    # What they did
    type = models.ForeignKey(NotificationType)

    # Who/what they did it to
    target_content_type = models.ForeignKey(ContentType, related_name='notify_target', blank=True, null=True)
    target_object_id = models.UUIDField(blank=True, null=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    timestamp = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=True)
    emailed = models.BooleanField(default=False)

    class Meta:
        # Do we really want a default ordering? I'm not sure
        ordering = ('-timestamp', )
        app_label = 'notifications'

    def __str__(self):
        parts = [self.actor, self.type,
                 self.target, self.timesince()]
        return ";".join(map(str, parts))

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        from django.utils.timesince import timesince as timesince_
        return timesince_(self.timestamp, now)


class NotificationSettings(models.Model):
    user = models.ForeignKey(User)
    entity = models.CharField(max_length=50)

    object_content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.UUIDField(null=True)
    object = GenericForeignKey('object_content_type', 'object_id')

    enabled = models.BooleanField(default=True)
    emails_enabled = models.BooleanField(default=True)
    email_address = models.ForeignKey(Email, null=True)

