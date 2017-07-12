import factory
from factory import fuzzy
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from users.models import UserProfile, Email
from users.signals import create_user_ssh_key

User = get_user_model()


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username', 'email')

    username = factory.Sequence(lambda o: 'user{}'.format(o))
    email = factory.Sequence(lambda o: 'user{}@a.pl'.format(o))
    password = factory.PostGenerationMethodCall('set_password', 'default')

    @classmethod
    def _generate(cls, create, attrs):
        post_save.disconnect(create_user_ssh_key, User)
        user = super()._generate(create, attrs)
        Token.objects.create(user=user)
        post_save.connect(create_user_ssh_key, User)
        return user


class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Email
    user = factory.SubFactory(UserFactory)
    address = fuzzy.FuzzyText(length=255)
    public = fuzzy.FuzzyChoice([True, False])
    unsubscribed = fuzzy.FuzzyChoice([True, False])
