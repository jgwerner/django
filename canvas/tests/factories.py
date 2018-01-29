import factory
from oauth2_provider.models import Application

from users.tests.factories import UserFactory


class ApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Application

    user = factory.SubFactory(UserFactory)
    client_type = Application.CLIENT_CONFIDENTIAL
    authorization_grant_type = Application.GRANT_CLIENT_CREDENTIALS
    name = factory.Sequence(lambda n: f'application_{n}')
