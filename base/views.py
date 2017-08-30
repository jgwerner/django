from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


class UUIDRegexMixin(object):
    lookup_value_regex = '[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}'


class NamespaceMixin(object):
    def get_queryset(self):
        return super().get_queryset().namespace(self.request.namespace)


class ProjectMixin(UUIDRegexMixin):
    def get_queryset(self):
        return super().get_queryset().filter(server__project_id=self.kwargs.get('project_pk'))


class ServerMixin(UUIDRegexMixin):
    def get_queryset(self):
        return super().get_queryset().filter(server_id=self.kwargs.get('server_pk'))


class RequestUserMixin(object):
    def _get_request_user(self):
        return self.context['request'].user

    def create(self, validated_data):
        instance = self.Meta.model(user=self._get_request_user(), **validated_data)
        instance.save()
        return instance


class LookupByMultipleFields(object):
    def get_object(self):
        qs = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        obj = qs.filter_by_name_or_id(self.kwargs[lookup_url_kwarg]).get()
        self.check_object_permissions(self.request, obj)
        return obj


@api_view(["GET"])
@permission_classes((AllowAny,))
def tbs_status(request, *args, **kwargs):
    return Response(status=status.HTTP_200_OK)
