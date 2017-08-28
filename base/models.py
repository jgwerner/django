from django.db.models import QuerySet

from .utils import validate_uuid


class TBSQuerySet(QuerySet):
    def tbs_filter(self, value):
        if validate_uuid(value):
            return self.filter(pk=value)
        return self.filter(**{self.model.LOOKUP_FIELD: value})
