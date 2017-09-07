import factory

from infrastructure.models import DockerHost
from users.tests.factories import UserFactory


class DockerHostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DockerHost

    name = factory.Sequence(lambda n: f'resource_{n}')
    ip = '127.0.0.1'
    port = 2375
    owner = factory.SubFactory(UserFactory)
