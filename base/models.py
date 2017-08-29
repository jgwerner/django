from django.db.models import QuerySet

from .utils import validate_uuid


class TBSQuerySet(QuerySet):
    def filter_by_name_or_id(self, value):
        if validate_uuid(value):
            return self.filter(pk=value)
        return self.filter(**{self.model.NATURAL_KEY: value})
