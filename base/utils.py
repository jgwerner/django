from uuid import UUID
from django.http import Http404


def validate_uuid(uuid):
    try:
        parsed = UUID(uuid)
    except ValueError:
        return False
    return str(parsed) == uuid


def get_object_or_404(model, val):
    try:
        obj = model.objects.filter_by_name_or_id(val).get()
    except model.DoesNotExist:
        raise Http404('No %s matches the given query.' % model._meta.object_name)
    return obj
