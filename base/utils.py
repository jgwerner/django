import sys
from io import TextIOWrapper
from uuid import UUID
from django.http import Http404
from logging import Logger


def validate_uuid(uuid):
    try:
        parsed = UUID(uuid)
    except ValueError:
        return False
    return str(parsed) == uuid


def get_object_or_404(model, val):
    try:
        obj = model.objects.tbs_filter(val).get()
    except model.DoesNotExist:
        raise Http404('No %s matches the given query.' % model._meta.object_name)
    return obj


def print_and_log(message: str, logger: Logger,
                  log_level: str="info", output_stream: TextIOWrapper=sys.stdout) -> None:
    print(message, file=output_stream)
    getattr(logger, log_level)(message)
