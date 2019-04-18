from uuid import uuid4
import factory
from factory import fuzzy
from django.contrib.auth import get_user_model

from appdj.base.tests.factories import FuzzyEmail
from ..models import UserProfile, Email

User = get_user_model()


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username', 'email')

    @factory.sequence
    def username(n):
        return f"user_{str(uuid4())[:16]}"

    email = FuzzyEmail()
    password = factory.PostGenerationMethodCall('set_password', 'default')

    @classmethod
    def _generate(cls, create, attrs):
        user = super()._generate(create, attrs)
        user.is_staff = True
        user.save()
        return user


class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Email
    user = factory.SubFactory(UserFactory)
    address = FuzzyEmail()
    public = fuzzy.FuzzyChoice([True, False])
    unsubscribed = fuzzy.FuzzyChoice([True, False])
