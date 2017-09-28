from django.conf.urls import url
from .views import NotificationViewSet

urlpatterns = [
    url(r'^$',
        NotificationViewSet.as_view({'get': 'list', 'patch': 'partial_update'}),
        name='notification-list'),
    url(r'^(?P<pk>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
        NotificationViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}),
        name='notification-detail'),
    url(r'^(?P<entity>[\w-]+)/$',
        NotificationViewSet.as_view({'get': 'list', 'patch': 'partial_update'}),
        name='notification-with-entity-list'),
    url(r'^(?P<entity>[\w-]+)/(?P<pk>[^/.]+)/$',
        NotificationViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}),
        name='notification-with-entity-detail'),


]
