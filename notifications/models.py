from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from users.models import User


class NotificationQuerySet(models.query.QuerySet):

    def unsent(self):
        return self.filter(emailed=False)

    def sent(self):
        return self.filter(emailed=True)

    def unread(self, include_deleted=False):
        """Return only unread items in the current queryset"""
        if not include_deleted:
            return self.filter(unread=True, deleted=False)
        else:
            """ when SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field.
            In this case, to improve query performance, don't filter by 'deleted' field
            """
            return self.filter(unread=True)

    def read(self, include_deleted=False):
        """Return only read items in the current queryset"""
        if not include_deleted:
            return self.filter(unread=False, deleted=False)
        else:
            """ when SOFT_DELETE=False, developers are supposed NOT to touch 'deleted' field.
            In this case, to improve query performance, don't filter by 'deleted' field
            """
            return self.filter(unread=False)

    def mark_all_as_read(self, recipient=None):
        """Mark as read any unread messages in the current queryset.
        Optionally, filter these by recipient first.
        """
        # We want to filter out read ones, as later we will store
        # the time they were marked as read.
        qs = self.unread(True)
        if recipient:
            qs = qs.filter(recipient=recipient)

        return qs.update(unread=False)

    def mark_all_as_unread(self, recipient=None):
        """Mark as unread any read messages in the current queryset.
        Optionally, filter these by recipient first.
        """
        qs = self.read(True)

        if recipient:
            qs = qs.filter(recipient=recipient)

        return qs.update(unread=True)

    def mark_as_unsent(self, recipient=None):
        qs = self.sent()
        if recipient:
            qs = self.filter(recipient=recipient)
        return qs.update(emailed=False)

    def mark_as_sent(self, recipient=None):
        qs = self.unsent()
        if recipient:
            qs = self.filter(recipient=recipient)
        return qs.update(emailed=True)


class NotificationType(models.Model):
    entity = models.CharField(max_length=25)
    name = models.CharField(max_length=25)
    description = models.TextField()


# Create your models here.
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

    # Is also what they did?
    # Not sure these should actually be here
    action_object_content_type = models.ForeignKey(ContentType, blank=True, null=True,
                                                   related_name='notify_action_object')
    action_object_object_id = models.UUIDField(blank=True, null=True)
    action_object = GenericForeignKey('action_object_content_type', 'action_object_object_id')

    timestamp = models.DateTimeField(default=timezone.now)

    public = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    emailed = models.BooleanField(default=False)

    objects = NotificationQuerySet.as_manager()

    class Meta:
        # Do we really want a default ordering? I'm not sure
        ordering = ('-timestamp', )
        app_label = 'notifications'

    def __str__(self):
        parts = [self.actor, self.type,
                 self.action_object,
                 self.target, self.timesince()]
        return ";".join(map(str, parts))

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        from django.utils.timesince import timesince as timesince_
        return timesince_(self.timestamp, now)

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()

    def mark_as_unread(self):
        if not self.unread:
            self.unread = True
            self.save()