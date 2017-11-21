from base.models import TBSQuerySet


class ServerQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        return self.filter(server__project__collaborator__user=namespace.object)


class DeploymentQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        return self.filter(deployment__project__collaborator__user=namespace.object)
