import factory
import random

from datetime import timedelta
from django.utils import timezone
from factory import fuzzy

from users.tests.factories import UserFactory
from notifications.models import Notification, NotificationType, NotificationSettings


class NotificationTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NotificationType

    entity = fuzzy.FuzzyText(length=50)
    name = fuzzy.FuzzyText(length=50)
    description = fuzzy.FuzzyText(length=100)
    subject = fuzzy.FuzzyText(length=75)
    template_name = fuzzy.FuzzyText(length=100)


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    user = factory.SubFactory(UserFactory)
    read = fuzzy.FuzzyChoice([True, False, False, False])

    # I don't know of a good way to generate these randomly since they're generic
    # Users must specify themselves
    actor = None
    target = None

    type = factory.SubFactory(NotificationTypeFactory)

    timestamp = fuzzy.FuzzyDateTime(start_dt=(timezone.now() - timedelta(days=7)))
    is_active = True
    emailed = fuzzy.FuzzyChoice([True, False])


class NotificationSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NotificationSettings

    user = factory.SubFactory(UserFactory)
    entity = fuzzy.FuzzyText(length=50)
    object = None
    enabled = fuzzy.FuzzyChoice([True, True, True, False])
    emails_enabled = factory.LazyAttribute(lambda obj: False if not obj.enabled
                                                       else random.choice([True, False]))
    email_address = factory.LazyAttribute(lambda obj: obj.user.emails.first())
