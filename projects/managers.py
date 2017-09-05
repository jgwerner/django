from base.models import TBSQuerySet
from base.utils import validate_uuid


class ProjectQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        return self.filter(collaborator__user=namespace.object)


class CollaboratorQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        return self.filter(user=namespace.object)

    def tbs_get(self, value):
        if validate_uuid(value):
            return self.get(user_id=value)
        return self.get(user__username=value)

    def _tbs_filter_str(self, value, *args, **kwargs):
        if validate_uuid(value):
            return self.filter(*args, user_id=value, **kwargs)
        return self.filter(*args, user__username=value, **kwargs)

    def _tbs_filter_iterable(self, value, *args, **kwargs):
        uuids = [val for val in value if validate_uuid(val)]
        natural_keys = [val for val in value if not validate_uuid(val)]
        return self.filter(*args, user_id__in=uuids, user__username__in=natural_keys, **kwargs)


class FileQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        return self.filter(author__username=namespace.name)


class SyncedResourceQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        return self.filter(project__collaborator__user=namespace.object)
