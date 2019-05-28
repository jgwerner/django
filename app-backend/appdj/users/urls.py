from django.conf.urls import url, include
from rest_framework_nested import routers
from . import views as user_views

user_router = routers.SimpleRouter()
user_router.register(r'profiles', user_views.UserViewSet)
user_router.register(r'(?P<user_id>[\w-]+)/emails', user_views.EmailViewSet)
user_router.register(r'integrations', user_views.IntegrationViewSet)

urlpatterns = [
    url(r'^users/', include(user_router.urls)),
    url(r'^users/(?P<user_pk>[\w-]+)/api-key/$', user_views.api_key, name='api_key'),
    url(r'^users/(?P<user_pk>[\w-]+)/avatar/$', user_views.avatar, name='avatar')
]
