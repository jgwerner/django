from django.conf.urls import url, include
from rest_framework_nested import routers
from appdj.projects.urls import project_router
from . import views as servers_views

servers_router = routers.SimpleRouter()
servers_router.register("options/server-size", servers_views.ServerSizeViewSet)

server_router = routers.NestedSimpleRouter(project_router, r'servers', lookup='server')
server_router.register(r'run-stats', servers_views.ServerRunStatisticsViewSet)
server_router.register(r'stats', servers_views.ServerStatisticsViewSet)

urlpatterns = [
    url(r'^(?P<namespace>[\w-]+)/', include(server_router.urls)),
    url(r'^servers/', include(servers_router.urls)),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/api-key/$',
        servers_views.server_key, name='server-api-key'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/api-key/reset/$',
        servers_views.server_key_reset, name='server-api-key-reset'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/start/$',
        servers_views.start, name='server-start'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/stop/$',
        servers_views.stop, name='server-stop'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/terminate/$',
        servers_views.terminate, name='server-terminate'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/api-key/verify/$',
        servers_views.VerifyJSONWebTokenServer.as_view(), name='server-api-key-verify'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/auth/$',
        servers_views.check_token, name='server-auth'),
]
