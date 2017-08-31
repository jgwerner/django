from django.db.models import QuerySet

from .utils import validate_uuid


class TBSQuerySet(QuerySet):
    def tbs_filter(self, value, *args, **kwargs):
        if validate_uuid(value):
            return self.filter(*args, pk=value, **kwargs)
        return self.filter(*args, **{self.model.NATURAL_KEY: value}, **kwargs)

    def tbs_get(self, value):
        if validate_uuid(value):
            return self.get(pk=value)
        return self.get(**{self.model.NATURAL_KEY: value})
