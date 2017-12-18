from servers.consumers import ServerStatusConsumer

routing = [ServerStatusConsumer.as_route(
    path=r'^/(?P<version>v\d+)/(?P<namespace>[\w-]+)/projects/(?P<project>[\w-]+)/servers/(?P<server>[\w-]+)/status/')]
