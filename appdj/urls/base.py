from django.conf.urls import url, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from oauth2_provider import views as oauth2_views
from jwt_auth import views as jwt_views
from users import views as user_views
from base.swagger.views import get_swagger_view

schema_view = get_swagger_view(title='3blades API', url=settings.FORCE_SCRIPT_NAME or '/')

urlpatterns = [
    url(r'^auth/jwt-token-auth/$', jwt_views.ObtainJSONWebToken.as_view(), name='obtain-jwt'),
    url(r'^auth/jwt-token-refresh/$', jwt_views.RefreshJSONWebToken.as_view(), name='refresh-jwt'),
    url(r'^auth/jwt-token-verify/$', jwt_views.VerifyJSONWebToken.as_view(), name='verify-jwt'),
    url(r'^auth/register/$', user_views.RegisterView.as_view(), name='register'),
    url(r'^auth/authorize/?$', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    url(r'^auth/token/?$', oauth2_views.TokenView.as_view(), name="token"),
    url(r'^auth/', include('social_django.urls', namespace="social")),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^swagger/$', schema_view),
    url(r'^(?P<version>{major_version}(\.[0-9]+)?)/'.format(major_version=settings.DEFAULT_VERSION),
        include("appdj.urls.unversioned"))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^auth/simple-token-auth/$', user_views.ObtainAuthToken.as_view()),
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns = staticfiles_urlpatterns() + urlpatterns