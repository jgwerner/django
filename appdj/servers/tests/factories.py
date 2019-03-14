import random
import factory
from django.utils import timezone
from datetime import timedelta
from factory import fuzzy

from appdj.projects.tests.factories import ProjectFactory
from .. import models
from appdj.users.tests.factories import UserFactory
from appdj.jwt_auth.utils import create_server_jwt


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
    image_name = 'illumidesk/datascience-notebook'
    is_active = True
    config = {'type': 'proxy'}

    @factory.post_generation
    def access_token(self, create, extracted, **kwargs):
        self.access_token = create_server_jwt(self.created_by, str(self.pk))
        self.save()


class ServerRunStatisticsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ServerRunStatistics

    server = factory.SubFactory(ServerFactory)
    start = timezone.now() - timedelta(hours=1)
    stop = timezone.now()
    duration = factory.LazyAttribute(lambda obj: obj.stop - obj.start if obj.stop else None)
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


class RuntimeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Runtime

    name = 'python2.7'


class FrameworkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Framework

    name = 'Tensorflow'
    version = '1.4'


class DeploymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Deployment

    name = factory.Sequence(lambda n: f'deployment_{n}')
    project = factory.SubFactory(ProjectFactory)
    created_by = factory.SubFactory(UserFactory)
    is_active = True
    framework = factory.SubFactory(FrameworkFactory)
    runtime = factory.SubFactory(RuntimeFactory)
