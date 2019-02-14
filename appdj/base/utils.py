import sys
from io import TextIOWrapper
import logging
from logging import Logger
from pathlib import Path
import shutil
import ujson
from uuid import UUID
import os

from django.http import Http404
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils.encoding import force_bytes, force_text
from django_redis.serializers.base import BaseSerializer

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


logger = logging.getLogger(__name__)


alphanumeric = RegexValidator(r'^[0-9a-zA-Z-]*$', "You can use only alphanumeric characters.")

def copy_model(model):
    if model is None:
        return
    new_object = model.__class__.objects.get(pk=model.pk)
    new_object.pk = None
    return new_object


def create_ssh_key(user):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    user_ssh_dir = Path(settings.RESOURCE_DIR, user.username, '.ssh')
    if not user_ssh_dir.exists():
        user_ssh_dir.mkdir(parents=True, exist_ok=True)
    user_ssh_private_key_file = user_ssh_dir.joinpath("id_rsa")
    if user_ssh_private_key_file.exists():
        os.remove(user_ssh_private_key_file)
    user_ssh_private_key_file.touch()
    user_ssh_private_key_file.write_bytes(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))
    user_ssh_public_key_file = user_ssh_dir.joinpath("id_rsa.pub")
    user_ssh_public_key_file.touch()
    user_ssh_public_key_file.write_bytes(public_key.public_bytes(
        serialization.Encoding.OpenSSH,
        serialization.PublicFormat.OpenSSH
    ))
    user_ssh_dir.chmod(0o770)
    user_ssh_private_key_file.chmod(0o440)
    user_ssh_public_key_file.chmod(0o600)


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


def print_and_log(message: str, logger: Logger,
                  log_level: str="info", output_stream: TextIOWrapper=sys.stdout) -> None:
    print(message, file=output_stream)
    getattr(logger, log_level)(message)


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
