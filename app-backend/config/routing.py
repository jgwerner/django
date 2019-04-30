from channels.routing import ProtocolTypeRouter, URLRouter
from appdj.servers.consumers import ServerStatusConsumer
from django.conf.urls import url

routing = [url(
    r'^(?P<version>v\d+)/(?P<namespace>[\w-]+)/projects/(?P<project>[\w-]+)/servers/(?P<server>[\w-]+)/status/$',
    ServerStatusConsumer
)]

application = ProtocolTypeRouter({
    'websocket': URLRouter(routing),
})
