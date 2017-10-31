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

from users import views as user_views
from triggers import views as trigger_views
from search.views import SearchView
from projects import views as project_views

router = routers.DefaultRouter()
router.register(r'projects', project_views.ProjectViewSet)
router.register(r'triggers', trigger_views.TriggerViewSet)
router.register(r'service/(?P<server>[^/.]+)/trigger', trigger_views.ServerActionViewSet)

urlpatterns = [
    url(r'^me/$', user_views.me, name="me"),
    url(r'^(?P<namespace>[\w-]+)/search/$', SearchView.as_view(), name='search'),
    url(r'^actions/', include('actions.urls')),
    url(r'^(?P<namespace>[\w-]+)/notifications/', include('notifications.urls')),
    url(r'^(?P<namespace>[\w-]+)/', include(router.urls)),
    # Below added by ncompton. Verify these work
    url(r'^(?P<namespace>[\w-]+)/', include('servers.urls')),
    url(r'^', include('billing.urls')),
    url(r'^', include('notifications.urls')),
    url(r'^', include('projects.urls')),
    url(r'^', include('servers.urls')),
    url(r'^', include('triggers.urls')),
    url(r'^', include('users.urls'))
]

@api_view()
def handler404(request):
    raise NotFound()


@api_view()
def handler500(request):
    raise APIException(detail="Internal Server Error", code=500)


if settings.DEBUG:
    urlpatterns = staticfiles_urlpatterns() + urlpatterns
