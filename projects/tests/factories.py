import factory
from users.tests.factories import UserFactory
from projects.models import Project, Collaborator


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda o: 'project{}'.format(o))
    is_active = True
    # copying_enabled = fuzzy.FuzzyChoice([True, False])


class CollaboratorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Collaborator

    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)
    owner = True
