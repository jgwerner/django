import logging
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import viewsets, status, permissions, exceptions
from rest_framework.response import Response
from rest_framework.decorators import api_view

from base.views import NamespaceMixin, LookupByMultipleFields
from projects.serializers import (ProjectSerializer,
                                  CollaboratorSerializer)
from projects.models import Project, Collaborator
from projects.permissions import ProjectPermission, ProjectChildPermission, has_project_permission
from projects.utils import (has_copy_permission,
                            perform_project_copy,
                            check_project_name_exists)
from teams.permissions import TeamGroupPermission

User = get_user_model()

log = logging.getLogger('projects')


class ProjectViewSet(LookupByMultipleFields, NamespaceMixin, viewsets.ModelViewSet):
    queryset = Project.objects.filter(is_active=True)
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, ProjectPermission, TeamGroupPermission)
    filter_fields = ('private', 'name')
    ordering_fields = ('name',)
    lookup_url_kwarg = 'project'

    def get_object(self):
        project = None
        all_projects = self.get_queryset()
        collab = Collaborator.objects.filter(project__in=all_projects,
                                             user=self.request.namespace.object).first()
        if collab is not None:
            project = collab.project
        if project is None:
            raise exceptions.NotFound()
        if has_project_permission(self.request, project):
            return project
        raise exceptions.PermissionDenied()

    def get_queryset(self):
        filter_name = self.request.query_params.get('name')
        filter_dict = {}
        if filter_name:
            filter_dict = {'name': filter_name}
        projects = Project.objects.namespace(self.request.namespace).tbs_filter(self.kwargs.get('project'),
                                                                                **filter_dict)
        if self.request.user != self.request.namespace.object:
            projects = projects.filter(Q(private=False) | Q(collaborator__user=self.request.user))
        return projects

    def _update(self, request, partial, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if not user.has_perm("projects.write_project", instance):
            return Response(data={'message': "Insufficient permissions to modify project"},
                            status=status.HTTP_403_FORBIDDEN)

        update_data = request.data

        context = self.get_serializer_context()
        context.update({'pk': instance.pk})
        serializer = self.serializer_class(instance, data=update_data,
                                           partial=partial,
                                           context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data,
                        status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        return self._update(request, False, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self._update(request, True, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        is_owner = Collaborator.objects.filter(project=instance,
                                               user=user,
                                               owner=True)
        if not is_owner.exists():
            return Response(data={'message': "Insufficient permissions to delete project"},
                            status=status.HTTP_403_FORBIDDEN)

        instance.is_active = False
        instance.save()
        return Response(data={"message": "Project deleted."},
                        status=status.HTTP_204_NO_CONTENT)


@api_view(['post'])
def project_copy(request, *args, **kwargs):
    proj_identifier = request.data['project']
    new_project_name = request.data.get('name')

    if new_project_name:
        log.info(f"Project name found in request during project copy. Validating name: {new_project_name}")
        if check_project_name_exists(new_project_name, request, None):
            log.exception(f"Project {new_project_name} already exists.")
            resp_status = status.HTTP_400_BAD_REQUEST
            resp_data = {'message': f"A project named {new_project_name} already exists."}
            return Response(data=resp_data, status=resp_status)

    try:
        # If user didn't provide a name, perform_project_copy() will handle duplicates appropriately
        new_project = perform_project_copy(user=request.user,
                                           project_id=proj_identifier,
                                           request=request,
                                           new_name=new_project_name)
    except Exception as e:
        log.exception(f"There was a problem attempting to copy project {proj_identifier}.", e)
        resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        resp_data = {'message': "Internal Server Error when attempting to copy project."}
    else:
        if new_project is not None:
            resp_status = status.HTTP_201_CREATED
            serializer = ProjectSerializer(instance=new_project)
            resp_data = serializer.data
        else:
            resp_status = status.HTTP_404_NOT_FOUND
            resp_data = {'message': f"Project {proj_identifier} not found."}
    return Response(data=resp_data, status=resp_status)


@api_view(['post'])
def project_copy_check(request, *args, **kwargs):
    has_perm = has_copy_permission(request=request)
    if has_perm:
        resp_status = status.HTTP_200_OK
    else:
        resp_status = status.HTTP_404_NOT_FOUND

    return Response(status=resp_status)


class ProjectMixin(LookupByMultipleFields):
    permission_classes = (permissions.IsAuthenticated, ProjectChildPermission, TeamGroupPermission)


class CollaboratorViewSet(ProjectMixin, viewsets.ModelViewSet):
    queryset = Collaborator.objects.all()
    serializer_class = CollaboratorSerializer
