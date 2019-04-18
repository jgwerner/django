"""
    projects URL Configuration

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

from config.urls.unversioned import router
from appdj.servers import views as servers_views
from . import views as project_views

project_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
project_router.register(r'collaborators', project_views.CollaboratorViewSet)
project_router.register(r'servers', servers_views.ServerViewSet)
project_router.register(r'deployments', servers_views.DeploymentViewSet)

urlpatterns = [
    url(r'^project-copy-check$',
        project_views.project_copy_check, name='project-copy-check'),
    url(r'^project-copy$', project_views.project_copy, name='project-copy'),
    url(r'^', include(project_router.urls))
]