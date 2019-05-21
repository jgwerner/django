import factory

from ..models import DockerHost, ECSCluster
from appdj.users.tests.factories import UserFactory


class DockerHostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DockerHost

    name = factory.Sequence(lambda n: f'resource_{n}')
    ip = '127.0.0.1'
    port = 2375
    owner = factory.SubFactory(UserFactory)



class ECSClusterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ECSCluster

    name = factory.Sequence(lambda n: f'cluster_{n}')
    created_by = factory.SubFactory(UserFactory)
