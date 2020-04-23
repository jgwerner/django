from django.urls import path
from . import views

from rest_framework import routers


app_name = 'teams'

urlpatterns = [
    path('', views.manage_teams, name='manage_teams'),
    path('list/', views.list_teams, name='list_teams'),
    path('create/', views.create_team, name='create_team'),
    path('<slug:team_slug>/manage/', views.manage_team, name='manage_team'),
    path('invitation/<slug:invitation_id>/', views.accept_invitation, name='accept_invitation'),
]

# drf config
router = routers.DefaultRouter()
router.register(r'api/teams', views.TeamViewSet)
router.register(r'api/invitations', views.InvitationViewSet)
urlpatterns += router.urls
