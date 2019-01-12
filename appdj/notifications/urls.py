"""
    notifications URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from .views import NotificationViewSet, NotificationSettingsViewset

urlpatterns = [
    url(r'^settings/$', NotificationSettingsViewset.as_view({'post': 'create',
                                                             'patch': 'partial_update',
                                                             'delete': 'destroy',
                                                             'get': 'retrieve'}),
        name='notification-settings'),
    url(r'^settings/entity/(?P<entity>[\w-]+)/$', NotificationSettingsViewset.as_view({'post': 'create',
                                                                                       'patch': 'partial_update',
                                                                                       'delete': 'destroy',
                                                                                       'get': 'retrieve'}),
        name='notification-settings-with-entity'),
    url(r'^$',
        NotificationViewSet.as_view({'get': 'list', 'patch': 'partial_update'}),
        name='notification-list'),
    url(r'^(?P<pk>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
        NotificationViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}),
        name='notification-detail'),
    url(r'^entity/(?P<entity>[\w-]+)/$',
        NotificationViewSet.as_view({'get': 'list', 'patch': 'partial_update'}),
        name='notification-with-entity-list'),


]
