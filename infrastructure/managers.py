from base.models import TBSQuerySet


class DockerHostQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        if namespace.type == 'user':
            return self.filter(owner=namespace.object)
        return self.filter(owner=namespace.object.owner)
