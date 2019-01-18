import factory

from appdj.users.tests.factories import UserFactory
from appdj.teams.models import Team, Group


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda o: f'team{o}')
    created_by = factory.SubFactory(UserFactory)


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = ('name', 'team')

    name = factory.Sequence(lambda o: f'group{o}')
    team = factory.SubFactory(TeamFactory, groups=None)
    created_by = factory.SubFactory(UserFactory)
    depth = 1
