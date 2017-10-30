from rest_framework_nested import routers
from . import views as infra_views

router = routers.DefaultRouter()

router.register(r'hosts', infra_views.DockerHostViewSet)
