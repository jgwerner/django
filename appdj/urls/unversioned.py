"""
    appdj URL Configuration

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

from billing import views as billing_views
from infrastructure import views as infra_views
from projects import views as project_views
from search.views import SearchView
from triggers import views as trigger_views
from users import views as user_views

router = routers.SimpleRouter()
router.register(r'hosts', infra_views.DockerHostViewSet)
router.register(r'triggers', trigger_views.TriggerViewSet)
router.register(r'projects', project_views.ProjectViewSet)
router.register(r'triggers', trigger_views.TriggerViewSet)
router.register(r'service/(?P<server>[^/.]+)/trigger', trigger_views.ServerActionViewSet)

if settings.ENABLE_BILLING:
    # add billing routing
    router.register(r'billing/cards', billing_views.CardViewSet)
    router.register(r'billing/plans', billing_views.PlanViewSet)
    router.register(r'billing/subscriptions', billing_views.SubscriptionViewSet)
    router.register(r'billing/invoices', billing_views.InvoiceViewSet)
    router.register(r'billing/(?P<invoice_id>[\w-]+)/invoice-items', billing_views.InvoiceItemViewSet)

urlpatterns = [
    url(r'^me/$', user_views.me, name="me"),
    url(r'^(?P<namespace>[\w-]+)/search/$', SearchView.as_view(), name='search'),
    url(r'^actions/', include('actions.urls')),
    url(r'^(?P<namespace>[\w-]+)/notifications/', include('notifications.urls')),
    url(r'^(?P<namespace>[\w-]+)/', include(router.urls)),
    url(r'^(?P<namespace>[\w-]+)/', include('servers.urls')),
    url(r'^', include('billing.urls')),
    url(r'^', include('notifications.urls')),
    url(r'^(?P<namespace>[\w-]+)/projects/', include('projects.urls')),
    url(r'^', include('servers.urls')),
    url(r'^', include('teams.urls')),
    url(r'^', include('triggers.urls')),
    url(r'^', include('users.urls')),
]

@api_view()
def handler404(request):
    raise NotFound()

@api_view()
def handler500(request):
    raise APIException(detail="Internal Server Error", code=500)

if settings.DEBUG:
    urlpatterns = staticfiles_urlpatterns() + urlpatterns
