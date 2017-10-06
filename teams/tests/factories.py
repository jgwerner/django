import factory

from users.tests.factories import UserFactory
from teams.models import Team, Group


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda o: f'team{o}')
    created_by = factory.SubFactory(UserFactory)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for group in extracted:
                self.groups.add(group)

        owners, created = Group.objects.get_or_create(
            name='owners', team=self, defaults=dict(created_by=self.created_by))
        if created:
            owners.user_set.add(self.created_by)
            owners.save()


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = ('name', 'team')

    name = factory.Sequence(lambda o: f'group{o}')
    team = factory.SubFactory(TeamFactory, groups=None)
    created_by = factory.SubFactory(UserFactory)
