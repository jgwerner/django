from collections import OrderedDict
from haystack.query import EmptySearchQuerySet, SearchQuerySet
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.serializers import Serializer

from projects.serializers import ProjectSerializer
from users.serializers import UserSerializer
from servers.serializers import ServerSerializer


class SearchView(ListAPIView):
    pagination_class = LimitOffsetPagination
    serializer_class = Serializer  # to make schema generator happy

    serializers = {
        "projects": ProjectSerializer,
        "servers": ServerSerializer,
        "users": UserSerializer,
    }

    def list(self, request, *args, **kwargs):
        querysets = self.get_querysets()
        rep = {}
        for typ, qs in querysets.items():
            serializer_class = self.serializers[typ]
            serializer = serializer_class(qs, many=True, context={'request': request})
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(qs, request, view=self)
            result = OrderedDict()
            if page is not None:
                result['count'] = paginator.count
                result['next'] = paginator.get_next_link()
                result['previous'] = paginator.get_previous_link()
                result['results'] = serializer.to_representation(page)
            else:
                result['results'] = serializer.to_representation(qs)
            if result['results']:
                rep[typ] = result
        return Response(rep)

    def get_querysets(self):
        params = self.request.query_params
        types = self.serializers.keys()
        if 'type' in params:
            types = self.request.query_params.getlist('type')
        querysets = {typ: EmptySearchQuerySet() for typ in types}
        if 'q' in params and params['q']:
            for typ in types:
                model = self.serializers[typ].Meta.model
                querysets[typ] = SearchQuerySet().models(model).filter(content=params.get('q'))
        return querysets
