from base.models import TBSQuerySet


class DockerHostQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        user = namespace.object if namespace.type == 'user' else namespace.object.owner
        return self.filter(owner=user)
