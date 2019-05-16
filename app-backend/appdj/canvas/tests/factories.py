import uuid
import factory
from oauth2_provider.models import Application

from appdj.users.tests.factories import UserFactory
from ..models import CanvasInstance


class ApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Application

    user = factory.SubFactory(UserFactory)
    client_type = Application.CLIENT_CONFIDENTIAL
    authorization_grant_type = Application.GRANT_CLIENT_CREDENTIALS
    name = factory.Sequence(lambda n: f'application_{n}')


class CanvasInstanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CanvasInstance

    instance_guid = str(uuid.uuid4())
    name = factory.Sequence(lambda n: f'instance_{n}')
