from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import TemplateView

from rest_framework.documentation import include_docs_urls
from rest_framework.documentation import get_schemajs_view
from rest_framework.authtoken.views import obtain_auth_token


schemajs_view = get_schemajs_view(title='IllumiDesk API')

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('api/', include('config.api_router')),
    path('auth-token/', obtain_auth_token),
    path('accounts/', include('allauth.urls')),
    path('users/', include('illumidesk.users.urls')),
    path('subscriptions/', include('illumidesk.subscriptions.urls')),
    path('teams/', include('illumidesk.teams.urls')),
    path('', include('illumidesk.web.urls')),
    path('illumidesk/', include('illumidesk.examples.urls')),
    path('celery-progress/', include('celery_progress.urls')),
    path('schemajs/', schemajs_view, name='api_schemajs'),
    path('stripe/', include('djstripe.urls', namespace='djstripe')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            '400/',
            default_views.bad_request,
            kwargs={'exception': Exception('Bad Request!')},
        ),
        path(
            '403/',
            default_views.permission_denied,
            kwargs={'exception': Exception('Permission Denied')},
        ),
        path(
            '404/',
            default_views.page_not_found,
            kwargs={'exception': Exception('Page not Found')},
        ),
        path('500/', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
