from django.db.models import QuerySet

from .utils import validate_uuid


class TBSQuerySet(QuerySet):
    def filter_by_name_or_id(self, value, *args, **kwargs):
        if validate_uuid(value):
            return self.filter(pk=value)
        return self.filter(*args, **{self.model.NATURAL_KEY: value}, **kwargs)
