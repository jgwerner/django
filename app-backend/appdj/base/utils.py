import logging
import shutil
from uuid import UUID

from django.http import Http404
from django.core.validators import RegexValidator
from django.utils.encoding import force_bytes, force_text
from django_redis.serializers.base import BaseSerializer
import ujson


logger = logging.getLogger(__name__)

alphanumeric = RegexValidator(r'^[0-9a-zA-Z-]*$', "You can use only alphanumeric characters.")


def copy_model(model):  # pylint: disable=inconsistent-return-statements
    if model is None:
        return
    new_object = model.__class__.objects.get(pk=model.pk)
    new_object.pk = None
    return new_object


def deactivate_user(user):
    user.is_active = False
    if user.profile.resource_root().exists():
        logger.info(f"Deleting user {user.username}'s files from disk.")
        logger.info(f"Path to be deleted: {user.profile.resource_root()}")
        shutil.rmtree(str(user.profile.resource_root()))
    else:
        logger.info(f"User {user} had no files created yet. Nothing to delete.")


def google_access_token_decoder(resp_str):
    if isinstance(resp_str, bytes):
        resp_str = resp_str.decode('utf-8')
    return ujson.loads(resp_str)


def get_object_or_404(model, *args, **kwargs):
    try:
        obj = model.objects.tbs_filter(*args, **kwargs).get()
    except model.DoesNotExist:
        raise Http404('No %s matches the given query.' % model._meta.object_name)
    return obj


def validate_uuid(uuid):
    try:
        parsed = UUID(uuid)
    except ValueError:
        return False
    return str(parsed) == uuid


class UJSONSerializer(BaseSerializer):
    def dumps(self, value):
        return force_bytes(ujson.dumps(value))

    def loads(self, value):
        return ujson.loads(force_text(value))
