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

from projects import views as project_views
from servers import views as servers_views
from users import views as user_views
from infrastructure import views as infra_views
from triggers import views as trigger_views
from billing import views as billing_views
from search.views import SearchView

router = routers.DefaultRouter()

router.register(r'hosts', infra_views.DockerHostViewSet)
router.register(r'triggers', trigger_views.TriggerViewSet)

user_router = routers.SimpleRouter()
user_router.register(r'profiles', user_views.UserViewSet)
user_router.register(r'(?P<user_id>[\w-]+)/emails', user_views.EmailViewSet)
user_router.register(r'integrations', user_views.IntegrationViewSet)

router.register(r'projects', project_views.ProjectViewSet)
project_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
project_router.register(r'collaborators', project_views.CollaboratorViewSet)
project_router.register(r'servers', servers_views.ServerViewSet)
project_router.register(r'project_files', project_views.ProjectFileViewSet)
server_router = routers.NestedSimpleRouter(project_router, r'servers', lookup='server')
server_router.register(r'ssh-tunnels', servers_views.SshTunnelViewSet)
server_router.register(r'run-stats', servers_views.ServerRunStatisticsViewSet)
server_router.register(r'stats', servers_views.ServerStatisticsViewSet)
server_router.register(r'triggers', trigger_views.ServerActionViewSet)

if settings.ENABLE_BILLING:
    router.register(r'billing/cards', billing_views.CardViewSet)
    router.register(r'billing/plans', billing_views.PlanViewSet)
    router.register(r'billing/subscriptions', billing_views.SubscriptionViewSet)
    router.register(r'billing/invoices', billing_views.InvoiceViewSet)
    router.register(r'billing/(?P<invoice_id>[\w-]+)/invoice-items', billing_views.InvoiceItemViewSet)

router.register(r'service/(?P<server>[^/.]+)/trigger', trigger_views.ServerActionViewSet)

servers_router = routers.SimpleRouter()
servers_router.register("options/server-size", servers_views.ServerSizeViewSet)


urlpatterns = [
    url(r'^me/$', user_views.me, name="me"),
    url(r'^(?P<namespace>[\w-]+)/search/$', SearchView.as_view(), name='search'),
    url(r'^actions/', include('actions.urls')),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server_server>[^/.]+)/internal/(?P<service>[^/.]+)/$',
        servers_views.server_internal_details, name="server_internal"),
    url(r'^(?P<namespace>[\w-]+)/triggers/send-slack-message/$', trigger_views.SlackMessageView.as_view(),
        name='send-slack-message'),
    url(r'^(?P<namespace>[\w-]+)/triggers/(?P<trigger>[\w-]+)/start/$', trigger_views.start,
        name='trigger-start'),
    url(r'^(?P<namespace>[\w-]+)/triggers/(?P<trigger>[\w-]+)/stop/$', trigger_views.stop,
        name='trigger-stop'),
    url(r'^(?P<namespace>[\w-]+)/', include(router.urls)),
    url(r'^(?P<namespace>[\w-]+)/', include(project_router.urls)),
    url(r'^(?P<namespace>[\w-]+)/', include(server_router.urls)),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project>[\w-]+)/synced-resources/$',
        project_views.SyncedResourceViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^users/', include(user_router.urls)),
    url(r'^users/(?P<user_pk>[\w-]+)/ssh-key/$', user_views.ssh_key, name='ssh_key'),
    url(r'^users/(?P<user_pk>[\w-]+)/ssh-key/reset/$', user_views.reset_ssh_key,
        name='reset_ssh_key'),
    url(r'^users/(?P<user_pk>[\w-]+)/api-key/$', user_views.api_key, name='api_key'),
    url(r'^users/(?P<user_pk>[\w-]+)/avatar/$', user_views.avatar, name='avatar'),
    url(r'^(?P<namespace>[\w-]+)/service/(?P<server>[^/.]+)/trigger/(?P<pk>[^/.]+)/call/$',
        trigger_views.call_trigger, name='server-trigger-call'),
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
    url(r'^servers/', include(servers_router.urls)),
    url(r'^webhooks/incoming/billing/invoice_created/$', billing_views.stripe_invoice_created,
        name='stripe-invoice-created'),
    url(r'^webhooks/incoming/billing/invoice_upcoming/$', billing_views.stripe_invoice_upcoming,
        name='stripe-invoice-upcoming'),
    url(r'^webhooks/incoming/billing/invoice_payment_failed/$', billing_views.stripe_invoice_payment_failed,
        name='stripe-invoice-payment-failed'),
    url(r'^webhooks/incoming/billing/invoice_payment_success/$', billing_views.stripe_invoice_payment_success,
        name='stripe-invoice-payment-success'),
    url(r'^(?P<namespace>[\w-]+)/notifications/', include("notifications.urls"))

]


@api_view()
def handler404(request):
    raise NotFound()


@api_view()
def handler500(request):
    raise APIException(detail="Internal Server Error", code=500)


if settings.DEBUG:
    urlpatterns = staticfiles_urlpatterns() + urlpatterns
