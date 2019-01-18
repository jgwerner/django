"""appdj URL Configuration

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
from django.conf import settings
from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, APIException
from rest_framework_nested import routers

from appdj.projects import views as project_views
from appdj.servers import views as servers_views
from appdj.users import views as user_views
from appdj.triggers import views as trigger_views
from appdj.teams import views as team_views
from appdj.search.views import SearchView
from appdj.canvas.views import CanvasXML, Auth, ApplicationViewSet

router = routers.SimpleRouter()

router.register(r'triggers', trigger_views.TriggerViewSet)

user_router = routers.SimpleRouter()
user_router.register(r'profiles', user_views.UserViewSet)
user_router.register(r'(?P<user_id>[\w-]+)/emails', user_views.EmailViewSet)
user_router.register(r'integrations', user_views.IntegrationViewSet)

router.register(r'projects', project_views.ProjectViewSet)
project_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
project_router.register(r'collaborators', project_views.CollaboratorViewSet)
project_router.register(r'servers', servers_views.ServerViewSet)
project_router.register(r'deployments', servers_views.DeploymentViewSet)
server_router = routers.NestedSimpleRouter(project_router, r'servers', lookup='server')
server_router.register(r'ssh-tunnels', servers_views.SshTunnelViewSet)
server_router.register(r'run-stats', servers_views.ServerRunStatisticsViewSet)
server_router.register(r'stats', servers_views.ServerStatisticsViewSet)
server_router.register(r'triggers', trigger_views.ServerActionViewSet)


router.register(r'service/(?P<server>[^/.]+)/trigger', trigger_views.ServerActionViewSet)

teams_router = routers.SimpleRouter()
teams_router.register(r'teams', team_views.TeamViewSet)

teams_sub_router = routers.NestedSimpleRouter(teams_router, r'teams', lookup='team')
teams_sub_router.register(r'groups', team_views.GroupViewSet)

my_teams_router = routers.SimpleRouter()
my_teams_router.register(r'teams', team_views.TeamViewSet, base_name='my-team')
my_teams_sub_router = routers.NestedSimpleRouter(my_teams_router, r'teams', lookup='team')
my_teams_sub_router.register(r'groups', team_views.GroupViewSet, base_name='my-group')

servers_router = routers.SimpleRouter()
servers_router.register("options/server-size", servers_views.ServerSizeViewSet)

router.register('oauth/applications', ApplicationViewSet)


urlpatterns = [
    url(r'^lti.xml$', CanvasXML.as_view(), name='canvas-xml'),
    url(r'^lti/$', Auth.as_view(), name='lti-auth'),
    url(r'^(?P<namespace>[\w-]+)/lti/(?P<task_id>[\w-]+)/(?P<path>.*?/?\w+(?:\.\w+)+)$',
        servers_views.lti_ready, name='lti-task'),
    url(r'^me/$', user_views.me, name="me"),
    url(r'^projects/lti/select/$', project_views.file_selection, name='project-file-select'),
    url(r'^(?P<namespace>[\w-]+)/search/$', SearchView.as_view(), name='search'),
    url(r'^actions/', include('appdj.actions.urls')),
    url(r'^(?P<namespace>[\w-]+)/triggers/send-slack-message/$', trigger_views.SlackMessageView.as_view(),
        name='send-slack-message'),
    url(r'^(?P<namespace>[\w-]+)/triggers/(?P<trigger>[\w-]+)/start/$', trigger_views.start,
        name='trigger-start'),
    url(r'^(?P<namespace>[\w-]+)/triggers/(?P<trigger>[\w-]+)/stop/$', trigger_views.stop,
        name='trigger-stop'),
    url(r'^(?P<namespace>[\w-]+)/projects/git-clone/$', project_views.CloneGitProject.as_view(), name='git-clone'),
    url(r'^(?P<namespace>[\w-]+)/projects/project-copy-check/$',
        project_views.project_copy_check, name='project-copy-check'),
    url(r'^(?P<namespace>[\w-]+)/projects/project-copy/$', project_views.project_copy, name='project-copy'),
    url(r'^(?P<namespace>[\w-]+)/', include(router.urls)),
    url(r'^(?P<namespace>[\w-]+)/', include(project_router.urls)),
    url(r'^(?P<namespace>[\w-]+)/', include(server_router.urls)),
    url(r'^users/', include(user_router.urls)),
    url(r'^users/(?P<user_pk>[\w-]+)/ssh-key/$', user_views.ssh_key, name='ssh_key'),
    url(r'^users/(?P<user_pk>[\w-]+)/ssh-key/reset/$', user_views.reset_ssh_key,
        name='reset_ssh_key'),
    url(r'^users/(?P<user_pk>[\w-]+)/api-key/$', user_views.api_key, name='api_key'),
    url(r'^users/(?P<user_pk>[\w-]+)/avatar/$', user_views.avatar, name='avatar'),
    url(r'^me/', include(my_teams_router.urls)),
    url(r'^me/', include(my_teams_sub_router.urls)),
    url(r'^', include(teams_router.urls)),
    url(r'^', include(teams_sub_router.urls)),
    url(r'^(?P<namespace>[\w-]+)/service/(?P<server>[^/.]+)/trigger/(?P<pk>[^/.]+)/call/$',
        trigger_views.call_trigger, name='server-trigger-call'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/lti/assignment/(?P<assignment_id>\d+)/$',
        servers_views.submit_assignment, name='assignment'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/start/$',
        servers_views.start, name='server-start'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/stop/$',
        servers_views.stop, name='server-stop'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/terminate/$',
        servers_views.terminate, name='server-terminate'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/api-key/$',
        servers_views.server_key, name='server-api-key'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/api-key/reset/$',
        servers_views.server_key_reset, name='server-api-key-reset'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/api-key/verify/$',
        servers_views.VerifyJSONWebTokenServer.as_view(), name='server-api-key-verify'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/auth/$',
        servers_views.check_token, name='server-auth'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/deployments/(?P<deployment>[^/.]+)/deploy/$',
        servers_views.deploy_deployment, name='deploy'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/endpoint/proxy/lab/tree/(?P<path>.*?/?\w+(?:\.\w+)+)$',
        servers_views.lti_redirect, name='lti-redirect'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/(?P<path>.*?/?\w+(?:\.\w+)+)$',
        servers_views.lti_file_handler, name='lti-file'),
    url(r'^servers/', include(servers_router.urls)),
    url(r'^(?P<namespace>[\w-]+)/notifications/', include("appdj.notifications.urls")),
    url(r'^(?P<namespace>[\w-]+)/teams/(?P<team_team>[\w-]+)/groups/(?P<group>[^/.]+)/add/',
        team_views.add_user_to_group, name='add-user-to-group'),
    url(r'^(?P<namespace>[\w-]+)/teams/(?P<team_team>[\w-]+)/groups/(?P<group>[^/.]+)/remove/',
        team_views.remove_user_from_group, name='remove-user-from-group'),
    url(r'^(?P<namespace>[\w-]+)/notifications/', include("appdj.notifications.urls"))
]


@api_view()
def handler404(request):
    raise NotFound()


@api_view()
def handler500(request):
    raise APIException(detail="Internal Server Error", code=500)


if settings.DEBUG:
    urlpatterns = staticfiles_urlpatterns() + urlpatterns
