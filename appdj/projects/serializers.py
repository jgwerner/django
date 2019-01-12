from django.contrib.auth import get_user_model
from django.db.models import Q
from guardian.shortcuts import assign_perm
from rest_framework import serializers

from appdj.base.serializers import SearchSerializerMixin
from appdj.projects.models import Project, Collaborator
from .utils import create_ancillary_project_stuff, check_project_name_exists
from .tasks import clone_git_repo
from servers.utils import stop_all_servers_for_project
from servers.models import Server

User = get_user_model()


class ProjectSerializer(SearchSerializerMixin, serializers.ModelSerializer):
    owner = serializers.CharField(source='get_owner_name', read_only=True)
    collaborators = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'private', 'last_updated', 'team', 'owner',
                  'collaborators', 'copying_enabled', 'config')
        read_only_fields = ('team', 'config')

    def validate_name(self, value):
        request = self.context['request']
        existing_pk = self.context['view'].kwargs.get('project')

        if check_project_name_exists(value, request, existing_pk):
            raise serializers.ValidationError("You can have only one project named %s" % value)
        return value

    def create(self, validated_data):
        project = super().create(validated_data)
        request = self.context['request']
        create_ancillary_project_stuff(request, project)
        return project


class FileAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')
        read_only_fields = ('email', 'username')


class CollaboratorServerSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='config.type')

    class Meta:
        model = Server
        fields = ('name', 'type')


class CollaboratorSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    member = serializers.CharField(write_only=True)
    permissions = serializers.MultipleChoiceField(choices=Project._meta.permissions)
    servers = CollaboratorServerSerializer(many=True, read_only=True, source='project.servers')

    class Meta:
        model = Collaborator
        fields = ('id', 'owner', 'project', 'user', 'joined', 'username', 'email', 'first_name', 'last_name',
                  'member', 'permissions', 'servers')
        read_only_fields = ('project', 'user')

    def validate_member(self, value):
        if not User.objects.filter(Q(username=value) | Q(email=value), is_active=True).exists():
            raise serializers.ValidationError("User %s does not exists" % value)
        return value

    def create(self, validated_data):
        permissions = validated_data.pop('permissions', ['read_project'])
        member = validated_data.pop('member')
        project = self._get_project() 
        owner = validated_data.get("owner", False)
        user = User.objects.filter(Q(username=member) | Q(email=member), is_active=True).first()

        if owner is True:
            updated = Collaborator.objects.filter(project=project).exclude(user=user).update(owner=False)
            if updated:
                stop_all_servers_for_project(project)

        # Ensure that owners and users with write permissions get read permissions as well.
        # For some reason, they come through as a set instead of a list
        if permissions == {'write_project'} or owner:
            permissions = {'write_project', 'read_project'}
        for permission in permissions:
            assign_perm(permission, user, project)
        return Collaborator.objects.create(user=user, project=project, **validated_data)

    def update(self, instance, validated_data):
        project = self._get_project() 
        owner = validated_data.get('owner', False)
        if owner is True:
            updated = Collaborator.objects.filter(project=project).exclude(user=instance.user).update(owner=False)
            if updated:
                stop_all_servers_for_project(project)
        return super().update(instance, validated_data)

    def _get_project(self):
        project_id = self.context['view'].kwargs['project_project']
        return Project.objects.tbs_get(project_id)


class CloneGitProjectSerializer(ProjectSerializer):
    url = serializers.URLField(write_only=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ('url',)

    def create(self, validated_data):
        url = validated_data.pop('url')
        project = super().create(validated_data)
        project.resource_root().mkdir(parents=True, exist_ok=True)
        clone_git_repo.delay(url, str(project.resource_root()))
        return project
