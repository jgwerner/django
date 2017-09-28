from base.models import TBSQuerySet


class DockerHostQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        return self.filter(owner=namespace.object)
