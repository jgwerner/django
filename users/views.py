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

from base.permissions import DeleteAdminOnly, PostAdminOnly
from base.views import LookupByMultipleFields
from utils import create_ssh_key, deactivate_user

from base.utils import get_object_or_404, validate_uuid
from users.filters import UserSearchFilter
from users.models import Email
from users.serializers import (UserSerializer,
                               EmailSerializer,
                               IntegrationSerializer)
from jwt_auth.utils import create_auth_jwt
from billing.models import Subscription
from billing.stripe_utils import cancel_subscriptions

log = logging.getLogger("users")
User = get_user_model()


class UserViewSet(LookupByMultipleFields, viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True).select_related('profile')
    serializer_class = UserSerializer
    filter_fields = ('username', 'email')
    permission_classes = (IsAuthenticated, PostAdminOnly)
    lookup_url_kwarg = 'user'

    def _update(self, request, partial, *args, **kwargs):
        data = request.data
        url_kwarg = kwargs.get(self.lookup_url_kwarg)
        user = User.objects.tbs_filter(url_kwarg).first()
        log.debug(user)

        # The given User exists, and there is an attempt to change the username
        # User could be none if the client is using PUT to create a user.
        if user is not None and request.data.get("username", user.username) != user.username:
            return Response(data={'message': "Username cannot be changed after creation."},
                            status=status.HTTP_400_BAD_REQUEST)

        if user is not None and "email" in data:
            if data['email'] == user.email:
                data.pop("email")

        serializer = self.get_serializer(instance=user, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if user is None:
            # A user is being created via PUT
            response_status = status.HTTP_201_CREATED
        else:
            response_status = status.HTTP_200_OK

        if validate_uuid(url_kwarg):
            serializer.save(id=url_kwarg)
        else:
            serializer.save(username=url_kwarg)

        user = serializer.instance
        user.is_active = True
        user.save()

        return Response(data=serializer.data,
                        status=response_status)

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

    def _check_for_permission_to_destroy(self):
        request_user = self.request.user
        kwargs_user = self.kwargs.get("user")
        return (request_user.is_staff or
                str(request_user.pk) == kwargs_user
                or request_user.username == kwargs_user)

    def destroy(self, request, *args, **kwargs):
        if self._check_for_permission_to_destroy():
            instance = User.objects.tbs_get(kwargs.get('user'))
            deactivate_user(instance)
            sub_ids = Subscription.objects.filter(customer=instance.customer).values_list('id')
            cancel_subscriptions(sub_ids)
            instance.save()
            resp_status = status.HTTP_204_NO_CONTENT
        else:
            resp_status = status.HTTP_403_FORBIDDEN

        return Response(status=resp_status)


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
            data = UserSerializer(instance=user,
                                  context={'request': request}).data
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
    serialized_data = UserSerializer(request.user).data
    return Response(data=serialized_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def my_api_key(request, **kwargs):
    token = create_auth_jwt(request.user)
    return Response(data={'token': token})


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
    token = create_auth_jwt(user)
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
