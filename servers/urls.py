"""
    servers URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from rest_framework_nested import routers

from projects.urls import project_router
from triggers import views as trigger_views
from . import views as servers_views


server_router = routers.NestedSimpleRouter(project_router, r'servers', lookup='server')
server_router.register(r'ssh-tunnels', servers_views.SshTunnelViewSet)
server_router.register(r'run-stats', servers_views.ServerRunStatisticsViewSet)
server_router.register(r'stats', servers_views.ServerStatisticsViewSet)
server_router.register(r'triggers', trigger_views.ServerActionViewSet)

urlpatterns = [
    url(r'^(?P<namespace>[\w-]+)/', include(server_router.urls)),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server_server>[^/.]+)/internal/(?P<service>[^/.]+)/$',
        servers_views.server_internal_details, name="server_internal"),
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
    url(r'^servers/', include(servers_urls.servers_router.urls)),
]