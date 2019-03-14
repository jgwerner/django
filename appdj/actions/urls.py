"""
    actions URL Configuration

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

from .views import ActionList, cancel, ActionViewSet

urlpatterns = [
    url(r'^$', ActionList.as_view(), name='action-list'),
    url(r'^create/$', ActionViewSet.as_view({'post': 'create'}), name='action-create'),
    url(r'^(?P<pk>[\w-]+)/cancel/$', cancel, name='action-cancel'),
    url(r'^(?P<pk>[\w-]+)/$', ActionViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}),
        name='action-detail'),
]
