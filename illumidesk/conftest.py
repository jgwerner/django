import pytest

from illumidesk.users.models import IllumiDeskUser
from illumidesk.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> IllumiDeskUser:
    return UserFactory()
