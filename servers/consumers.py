import logging
from channels.generic.websockets import JsonWebsocketConsumer
from base.namespace import Namespace
from .models import Server
from projects.models import Project

log = logging.getLogger('servers')


class ServerStatusConsumer(JsonWebsocketConsumer):
    group_prefix = 'statuses'

    def connection_groups(self, **kwargs):
        namespace_arg = kwargs.get('namespace')
        server_arg = kwargs.get('server')
        project_arg = kwargs.get('project')
        namespace = Namespace.from_name(namespace_arg)
        project = Project.objects.namespace(namespace).tbs_filter(project_arg).first()
        try:
            server = Server.objects.filter(project=project).tbs_get(server_arg)
        except Server.DoesNotExist:
            self.close()
        return [f'{self.group_prefix}_{server.pk}']

    @classmethod
    def update_status(cls, server_id: str, status: str):
        cls.group_send(f'{cls.group_prefix}_{server_id}', {"status": status.title()})
