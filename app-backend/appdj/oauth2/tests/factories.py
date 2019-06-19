import factory

from oauth2_provider.models import Application


class ApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Application
