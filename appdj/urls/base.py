from django.conf.urls import url, include
from django.conf import settings
urlpatterns = [
    url(r'^(?P<version>{major_version}(\.[0-9]+)?)/'.format(major_version=settings.DEFAULT_VERSION),
        include("appdj.urls.unversioned"))
]
