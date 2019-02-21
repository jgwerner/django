from collections import OrderedDict
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector, TrigramSimilarity
from django.contrib.postgres.indexes import GinIndex
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.serializers import Serializer

from projects.serializers import ProjectSerializer
from projects.models import Project
from users.serializers import UserSerializer
from users.models import User
from servers.serializers import ServerSearchSerializer
from servers.serializers import Server


class SearchView(ListAPIView):
    pagination_class = LimitOffsetPagination
    serializer_class = Serializer  # to make schema generator happy

    # Objects available for searching
    searchable_objects = (
        (Project, ProjectSerializer),
        (Server, ServerSearchSerializer),
        (User, UserSerializer),
    )

    def list(self, request, *args, **kwargs):
        response_data = {}
        params = self.request.query_params
        if 'q' not in params or not params['q']:
            return Response({'error': "You must provide a query to search for"}, status=400)
        for (model, serializer_class) in self.searchable_objects:
            model_results = self.get_model_results(model, serializer_class)
            if model_results['results']:
                key = str(model._meta.verbose_name_plural)
                response_data[key] = model_results
        return Response(data=response_data)

    def get_model_qs(self, model):
        """
        Builds search queryset using postgres full text search feature
        """
        q = self.request.query_params['q']
        query = SearchQuery(q)
        search_fields = self._get_model_search_fields(model)
        vector = SearchVector(*search_fields)
        similarity = None
        for field in search_fields:
            if similarity is None:
                similarity = TrigramSimilarity(field, q)
            else:
                similarity += TrigramSimilarity(field, q)
        return model.objects.filter(is_active=True).annotate(
            rank=SearchRank(vector, query),
            similarity=similarity,
        ).filter(Q(rank__gte=0.3) | Q(similarity__gt=0.3)).order_by('-rank')

    def get_model_results(self, model, serializer_class):
        """
        Builds search results dict for model
        """
        queryset = self.get_model_qs(model)
        serializer = serializer_class(queryset, many=True,
                                      context={'request': self.request, 'view': self})
        page = self.paginate_queryset(queryset)
        results = OrderedDict()
        if page is not None:
            results['count'] = self.paginator.count
            results['next'] = self.paginator.get_next_link()
            results['previous'] = self.paginator.get_previous_link()
            results['results'] = serializer.to_representation(page)
        else:
            results['results'] = serializer.to_representation(queryset)
        return results

    def _get_model_search_fields(self, model): # pylint disable=no-self-use
        """
        Looks for search fields defined in gin index created on model
        """
        for index in model._meta.indexes:
            if isinstance(index, GinIndex):
                return index.fields
