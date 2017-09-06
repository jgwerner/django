from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


class NamespaceMixin:
    def get_queryset(self):
        return super().get_queryset().namespace(self.request.namespace)


class RequestUserMixin(object):
    def _get_request_user(self):
        return self.context['request'].user

    def create(self, validated_data):
        instance = self.Meta.model(user=self._get_request_user(), **validated_data)
        instance.save()
        return instance


def get_endswith(dic, key):
    keys = [k for k in dic.keys() if k.endswith(key)]
    if len(keys) > 1:
        raise KeyError(f"Multiple values for key: {key}")
    return dic[keys[0]]


class LookupByMultipleFields:
    def get_queryset(self):
        qs = super().get_queryset()
        filter_kwargs = {}
        if hasattr(qs.model, 'is_active'):
            filter_kwargs['is_active'] = True
        prepare_kwargs = {k.split('_')[-1] if '_' in k else k: v for k, v in self.kwargs.items()}
        parent_arg = next((x for x in prepare_kwargs if hasattr(qs.model, x)), None)
        if parent_arg:
            parent_model = getattr(qs.model, parent_arg).field.related_model
            parent_object = parent_model.objects.tbs_filter(prepare_kwargs[parent_arg]).first()
            filter_kwargs[parent_arg] = parent_object
        return qs.filter(**filter_kwargs) if filter_kwargs else qs

    def get_object(self):
        qs = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        try:
            obj = qs.tbs_get(self.kwargs[lookup_url_kwarg])
        except ObjectDoesNotExist:
            raise Http404
        self.check_object_permissions(self.request, obj)
        return obj


@api_view(["GET"])
@permission_classes((AllowAny,))
def tbs_status(request, *args, **kwargs):
    return Response(status=status.HTTP_200_OK)
