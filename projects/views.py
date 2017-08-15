import logging
from rest_framework import viewsets, status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from base.views import NamespaceMixin
from projects.serializers import (ProjectSerializer,
                                  CollaboratorSerializer,
                                  SyncedResourceSerializer,
                                  ProjectFileSerializer)
from projects.models import Project, Collaborator, SyncedResource
from projects.permissions import ProjectPermission, ProjectChildPermission
from projects.tasks import sync_github
from projects.models import ProjectFile
from projects.utils import get_files_from_request

log = logging.getLogger('projects')


class ProjectViewSet(NamespaceMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, ProjectPermission)
    filter_fields = ('private', 'name')
    ordering_fields = ('name',)

    def _update(self, request, partial,  *args, **kwargs):
        instance = Project.objects.get(pk=kwargs.get("pk"))
        user = request.user

        if not user.has_perm("projects.write_project", instance):
            return Response(data={'message': "Insufficient permissions to modify project"},
                            status=status.HTTP_403_FORBIDDEN)

        update_data = request.data

        serializer = self.serializer_class(instance, data=update_data,
                                           partial=partial,
                                           context={'request': request,
                                                    'pk': instance.pk})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data,
                        status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        return self._update(request, False, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self._update(request, True, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = Project.objects.get(pk=kwargs.get("pk"))
        user = request.user
        is_owner = Collaborator.objects.filter(project=instance,
                                               user=user,
                                               owner=True)
        if not is_owner.exists():
            return Response(data={'message': "Insufficient permissions to delete project"},
                            status=status.HTTP_403_FORBIDDEN)

        instance.delete()
        return Response(data={"message": "Project deleted."},
                        status=status.HTTP_204_NO_CONTENT)


class ProjectMixin(object):
    permission_classes = (permissions.IsAuthenticated, ProjectChildPermission)

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().filter(project_id=self.kwargs.get('project_pk'))


class CollaboratorViewSet(ProjectMixin, viewsets.ModelViewSet):
    queryset = Collaborator.objects.all()
    serializer_class = CollaboratorSerializer


class SyncedResourceViewSet(ProjectMixin, viewsets.ModelViewSet):
    queryset = SyncedResource.objects.all()
    serializer_class = SyncedResourceSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.status_code = status.HTTP_202_ACCEPTED
        return response

    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance
        sync_github.delay(
            str(instance.project.resource_root().joinpath(instance.folder)), self.request.user.pk, instance.project.pk,
            repo_url=instance.settings['repo_url'], branch=instance.settings.get('branch', 'master')
        )


class ProjectFileViewSet(ProjectMixin,
                         viewsets.ModelViewSet):
    queryset = ProjectFile.objects.all()
    serializer_class = ProjectFileSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self, *args, **kwargs):
        project_pk = kwargs.get("project_pk")
        queryset = ProjectFile.objects.filter(project__pk=project_pk)
        filename = self.request.query_params.get("filename", None)
        if filename is not None:
            complete_filename = "{usr}/{proj}/{file}".format(usr=self.request.user.username,
                                                             proj=project_pk,
                                                             file=filename)
            queryset = queryset.filter(file=complete_filename)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = ProjectFile.objects.get(project__pk=kwargs.get("project_pk"),
                                           pk=kwargs.get("pk"))
        get_content = self.request.query_params.get('content', "false").lower() == "true"
        serializer = self.serializer_class(instance,
                                           context={'get_content': get_content})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = ProjectFile.objects.get(project__pk=kwargs.get("project_pk"),
                                           pk=kwargs.get("pk"))
        data = {'id': instance.pk}
        instance.delete()
        data['deleted'] = True
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(*args, **kwargs)
        get_content = self.request.query_params.get('content', "false").lower() == "true"
        serializer = self.serializer_class(queryset, many=True, context={'get_content': get_content})
        data = serializer.data
        for proj_file in data:
            proj_file['file'] = request.build_absolute_uri(proj_file['file'])

        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        try:
            files = get_files_from_request(request)
        except ValueError as e:
            log.exception(e)
            data = {'message': str(e)}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        proj_files_to_serialize = []
        project_pk = kwargs.get("project_pk")

        for f in files:
            project = Project.objects.get(pk=project_pk)
            create_data = {'author': self.request.user,
                           'project': project,
                           'file': f}
            project_file = ProjectFile(**create_data)

            project_file.save()

            proj_files_to_serialize.append(project_file.pk)

        proj_files = ProjectFile.objects.filter(pk__in=proj_files_to_serialize)

        serializer = self.serializer_class(proj_files,
                                           context={'request': request},
                                           many=True)
        return Response(data=serializer.data,
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        try:
            files = get_files_from_request(request)
        except ValueError as e:
            log.exception(e)
            data = {'message': str(e)}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        if len(files) > 1:
            log.warning("There was an attempt to update more than one file.")
            return Response(data={'message': "Only one file can be updated at a time."},
                            status=status.HTTP_400_BAD_REQUEST)

        instance = ProjectFile.objects.get(pk=kwargs.get("pk"))
        project_pk = request.data.get("project")
        new_file = files[0]

        data = {'project': project_pk,
                'file': new_file}

        serializer = self.serializer_class(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data,
                        status=status.HTTP_200_OK)

