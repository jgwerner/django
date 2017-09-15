import logging
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from haystack.query import SearchQuerySet, EmptySearchQuerySet
from social_django.models import UserSocialAuth
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from base.permissions import DeleteAdminOnly, PostAdminOnly
from base.views import LookupByMultipleFields
from utils import create_ssh_key, deactivate_user, create_jwt_token

from base.utils import get_object_or_404, validate_uuid
from users.filters import UserSearchFilter
from users.models import Email
from users.serializers import (UserSerializer,
                               EmailSerializer,
                               IntegrationSerializer,
                               AuthTokenSerializer)

log = logging.getLogger("users")
User = get_user_model()


class UserViewSet(LookupByMultipleFields, viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True).select_related('profile')
    serializer_class = UserSerializer
    filter_fields = ('username', 'email')
    permission_classes = (IsAuthenticated, DeleteAdminOnly, PostAdminOnly)
    lookup_url_kwarg = 'user'

    def _update(self, request, partial, *args, **kwargs):
        data = request.data
        url_kwarg = kwargs.get(self.lookup_url_kwarg)
        user = User.objects.tbs_filter(url_kwarg).first()

        # The given User exists, and there is an attempt to change the username
        # User could be none if the client is using PUT to create a user.
        if user is not None and request.data.get("username", user.username) != user.username:
            return Response(data={'message': "Username cannot be changed after creation."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(instance=user, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if validate_uuid(url_kwarg):
            serializer.save(id=url_kwarg)
        else:
            serializer.save(username=url_kwarg)

        return Response(data=serializer.data,
                        status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = serializer.instance
        user.is_active = True
        user.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def partial_update(self, request, *args, **kwargs):
        return self._update(request, True, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return self._update(request, False, *args, **kwargs)

    def perform_destroy(self, instance):
        deactivate_user(instance)
        instance.save()


@csrf_exempt
def avatar(request, version, user_pk):
    status_code = status.HTTP_200_OK

    if request.method == "POST":
        try:
            user = User.objects.tbs_get(user_pk)
            profile = user.profile
            profile.avatar = request.FILES.get("image")
            profile.save()
            log.info("Updated avatar for user: {user}".format(user=user.username))
            data = UserSerializer(instance=user).data
        except Exception as e:
            data = {'message': str(e)}
            log.exception(e)
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        data = {'message': "Only POST is allowed for this URL."}
        status_code = status.HTTP_405_METHOD_NOT_ALLOWED

    return JsonResponse(data=data, status=status_code)


class UserSearchView(ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSerializer
    filter_class = UserSearchFilter

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        qs = EmptySearchQuerySet()
        if 'q' in self.request.GET:
            qs = SearchQuerySet().filter(content=self.request.GET.get('q', ''))
        return qs


class RegisterView(CreateAPIView):
    """
    User register
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = ()
    authentication_classes = ()


@api_view(['GET'])
def me(request, version):
    log.debug(("request.user", request.user))

@api_view(['GET'])
def ssh_key(request, version, user_pk):
    user = get_object_or_404(User, user_pk)
    return Response(data={'key': user.profile.ssh_public_key()})


@api_view(['POST'])
def reset_ssh_key(request, version, user_pk):
    user = get_object_or_404(User, user_pk)
    create_ssh_key(user)
    return Response(data={'key': user.profile.ssh_public_key()})


@api_view(['GET'])
def api_key(request, version, user_pk):
    user = get_object_or_404(User, user_pk)
    token = create_jwt_token(user)
    return Response(data={'token': token})


class EmailViewSet(viewsets.ModelViewSet):
    queryset = Email.objects.all()
    serializer_class = EmailSerializer

    def get_queryset(self):
        return super().get_queryset().filter(Q(user=self.request.user) | Q(public=True))

    def list(self, request, *args, **kwargs):
        emails = self.get_queryset().filter(user=User.objects.tbs_get(kwargs.get("user_id")))
        serializer = self.get_serializer(emails, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        email = self.get_queryset().filter(user=User.objects.tbs_get(kwargs.get("user_id")),
                                           pk=kwargs.get("pk")).first()
        serializer = self.get_serializer(email)
        data = serializer.data if email is not None else {}
        return Response(data)


class IntegrationViewSet(viewsets.ModelViewSet):
    queryset = UserSocialAuth.objects.all()
    serializer_class = IntegrationSerializer

    def create(self, request, *args, **kwargs):
        data = {'provider': request.data.get("provider"),
                'extra_data': request.data.get("extra_data"),
                'user': request.user}
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.create(validated_data=data)
        return Response(data=self.serializer_class(instance).data,
                        status=status.HTTP_201_CREATED)


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        from rest_framework.authtoken.models import Token
        serializer = self.get_serializer()
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        if created:
            log.info("Created a new token for {user}".format(user=user.username))

        return Response({'token': token.key}, status=201)

    def get_serializer(self):
        return self.serializer_class(data=self.request.data)
