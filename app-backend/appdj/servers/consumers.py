import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

logger = logging.getLogger(__name__)


class ServerStatusConsumer(JsonWebsocketConsumer):

    def connect(self):
        server_id = self.scope['url_route']['kwargs']['server']
        async_to_sync(self.channel_layer.group_add)(f"statuses_{server_id}", self.channel_name)
        super().connect()

    def disconnect(self, code):
        server_id = self.scope['url_route']['kwargs']['server']
        async_to_sync(self.channel_layer.group_discard)(f"statuses_{server_id}", self.channel_name)
        super().disconnect()

    def status_update(self, event):
        self.send_json(event)
