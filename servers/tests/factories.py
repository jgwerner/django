import random
import factory
from django.utils import timezone
from datetime import timedelta
from factory import fuzzy

from projects.tests.factories import ProjectFactory
from servers import models
from users.tests.factories import UserFactory


class ServerSizeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ServerSize

    name = factory.Sequence(lambda n: 'resource_{}'.format(n))
    cpu = random.randint(1, 9)
    memory = fuzzy.FuzzyChoice([512, 1024, 2048, 4096])
    active = True
    cost_per_second = fuzzy.FuzzyDecimal(low=0.0, high=0.1)


class ServerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Server

    private_ip = '127.0.0.1'
    public_ip = '127.0.0.1'
    name = factory.Sequence(lambda n: f'server_{n}')
    server_size = factory.SubFactory(ServerSizeFactory)
    project = factory.SubFactory(ProjectFactory)
    created_by = factory.SubFactory(UserFactory)
    image_name = '3blades/server'
    is_active = True
    config = {'type': 'proxy'}


class ServerRunStatisticsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ServerRunStatistics

    server = factory.SubFactory(ServerFactory)
    start = timezone.now() - timedelta(hours=1)
    stop = timezone.now()
    duration = factory.LazyAttribute(lambda obj: obj.stop - obj.start)
    exit_code = 0
    project = factory.LazyAttribute(lambda obj: obj.server.project)
    owner = factory.LazyAttribute(lambda obj: obj.server.project.owner)
    server_size_memory = factory.LazyAttribute(lambda obj: obj.server.server_size.memory)


class ServerStatisticsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ServerStatistics

    server = factory.SubFactory(ServerFactory)
    start = timezone.now() - timedelta(hours=1)
    stop = timezone.now()
    size = 0


class SSHTunnelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SshTunnel

    name = factory.Faker('name')
    host = factory.Faker('domain_name')
    local_port = factory.Faker('pyint')
    endpoint = factory.Faker('domain_name')
    remote_port = factory.Faker('pyint')
    username = factory.Faker('user_name')
    server = factory.SubFactory(ServerFactory)
