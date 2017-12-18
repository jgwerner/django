import logging
from channels.generic.websockets import JsonWebsocketConsumer
from base.namespace import Namespace
from .models import Server
from projects.models import Project

log = logging.getLogger('servers')


class ServerStatusConsumer(JsonWebsocketConsumer):
    group_prefix = 'statuses'

    def connection_groups(self, **kwargs):
        namespace = kwargs.get('namespace')
        server = kwargs.get('server')
        project = kwargs.get('project')
        self.namespace = Namespace.from_name(namespace)
        pr = Project.objects.namespace(self.namespace).tbs_filter(project).first()
        try:
            srv = Server.objects.filter(project=pr).tbs_get(server)
        except Server.DoesNotExist:
            self.close()
        return [f'{self.group_prefix}_{srv.pk}']

    @classmethod
    def update_status(cls, server_id: str, status: str):
        cls.group_send(f'{cls.group_prefix}_{server_id}', {"status": status.title()})
