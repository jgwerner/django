from collections import Iterable
from django.db.models import QuerySet

from .utils import validate_uuid


class TBSQuerySet(QuerySet):
    def tbs_filter(self, value, *args, **kwargs):
        """
        Filters objects against pk or natural key.
        :param value: PK or natural key
        :return: Django queryset
        """
        if isinstance(value, str):
            if validate_uuid(value):
                return self.filter(*args, pk=value, **kwargs)
            return self.filter(*args, **{self.model.NATURAL_KEY: value}, **kwargs)
        if isinstance(value, Iterable):
            uuids = [val for val in value if validate_uuid(val)]
            natural_keys = [val for val in value if not validate_uuid(val)]
            return self.filter(*args, **{'pk__in': uuids, f'{self.model.NATURAL_KEY}__in': natural_keys}, **kwargs)
        return self.filter(*args, **kwargs)

    def tbs_get(self, value):
        """
        Gets object by pk or natural key
        :param value: pk or natural key
        :return: django queryset
        """
        if validate_uuid(value):
            return self.get(pk=value)
        return self.get(**{self.model.NATURAL_KEY: value})
