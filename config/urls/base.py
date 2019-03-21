from django.conf.urls import url, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.conf.urls.static import static
from djoser import views as djoser_views

from appdj.jwt_auth import views as jwt_views
from appdj.base.views import tbs_status
from appdj.users import views as users_views
from appdj.servers import views as servers_views
from .unversioned import urlpatterns as unversioned_urls


urlpatterns = [
    url(r'^sns/$', servers_views.SNSView.as_view(), name='sns'),
    url(r'^auth/jwt-token-auth/$', jwt_views.ObtainJSONWebToken.as_view(), name='obtain-jwt'),
    url(r'^auth/temp-token-auth/$', users_views.my_api_key, name='temp-token-auth'),
    url(r'^auth/jwt-token-refresh/$', jwt_views.RefreshJSONWebToken.as_view(), name='refresh-jwt'),
    url(r'^auth/jwt-token-verify/$', jwt_views.VerifyJSONWebToken.as_view(), name='verify-jwt'),
    url(r'^auth/register/$', djoser_views.UserCreateView.as_view(), name='register'),
    url(r'^auth/activate/$', djoser_views.ActivationView.as_view(), name='activate'),
    url(r'^auth/password/reset/$', djoser_views.PasswordResetView.as_view(), name="password-reset"),
    url(r'^auth/', include('rest_framework_social_oauth2.urls')),
    url(r'^auth/password/reset/confirm/$', djoser_views.PasswordResetConfirmView.as_view(),
        name="password-reset-confirm"),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^tbs-admin/', admin.site.urls),
    url(r'^(?P<version>{major_version}(\.[0-9]+)?)/'.format(major_version=settings.DEFAULT_VERSION),
        include(unversioned_urls)),
    url(r'^tbs-status/', tbs_status, name="tbs-status")
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = staticfiles_urlpatterns() + urlpatterns
