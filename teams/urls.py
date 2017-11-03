"""
    teams URL Configuration

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
from rest_framework_nested import routers
from . import views as team_views

teams_router = routers.SimpleRouter()
teams_router.register(r'teams', team_views.TeamViewSet)

teams_sub_router = routers.NestedSimpleRouter(teams_router, r'teams', lookup='team')
teams_sub_router.register(r'groups', team_views.GroupViewSet)

my_teams_router = routers.SimpleRouter()
my_teams_router.register(r'teams', team_views.TeamViewSet, base_name='my-team')

my_teams_sub_router = routers.NestedSimpleRouter(my_teams_router, r'teams', lookup='team')
my_teams_sub_router.register(r'groups', team_views.GroupViewSet, base_name='my-group')

if settings.ENABLE_BILLING:
    teams_billing_router = routers.NestedSimpleRouter(teams_router, r'teams', lookup='team')
    teams_billing_router.register(r'billing/subscriptions', team_views.TeamSubscriptionViewSet, base_name='team-subscription')
    teams_billing_router.register(r'billing/invoices', team_views.TeamInvoiceViewSet, base_name='team-invoices')
    teams_billing_router.register(r'billing/(?P<invoice_id>[\w-]+)/invoice-items', team_views.TeamInvoiceItemViewSet, base_name='team-invoice-items')

urlpatterns = [
    url(r'^me/', include(my_teams_router.urls)),
    url(r'^me/', include(my_teams_sub_router.urls)),
    url(r'^', include(teams_router.urls)),
    url(r'^', include(teams_sub_router.urls)),
    url(r'^', include(teams_billing_router.urls)),
]