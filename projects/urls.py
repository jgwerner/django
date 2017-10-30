from django.conf.urls import url
from rest_framework_nested import routers

from . import views as project_views

router = routers.DefaultRouter()
router.register(r'projects', project_views.ProjectViewSet)

project_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
project_router.register(r'collaborators', project_views.CollaboratorViewSet)
project_router.register(r'project_files', project_views.ProjectFileViewSet)

urlpatterns = [
    url(r'^(?P<namespace>[\w-]+)/projects/project-copy-check/$',
        project_views.project_copy_check, name='project-copy-check'),
    url(r'^(?P<namespace>[\w-]+)/projects/project-copy/$', project_views.project_copy, name='project-copy'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project>[\w-]+)/synced-resources/$',
        project_views.SyncedResourceViewSet.as_view({'get': 'list', 'post': 'create'})),
]