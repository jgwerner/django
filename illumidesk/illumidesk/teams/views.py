from rest_framework import viewsets

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from illumidesk.teams.decorators import login_and_team_required
from illumidesk.teams.invitations import send_invitation

from .forms import TeamChangeForm
from .models import Invitation
from .models import Team
from .serializers import InvitationSerializer
from .serializers import TeamSerializer


@login_required
def manage_teams(request):
    return render(request, 'teams/teams.html', {})


@login_required
def list_teams(request):
    teams = request.user.teams.all()
    return render(request, 'teams/list_teams.html', {
        'teams': teams,
    })


@login_required
def create_team(request):
    if request.method == 'POST':
        form = TeamChangeForm(request.POST)
        if form.is_valid():
            team = form.save()
            team.members.add(request.user, through_defaults={'role': 'admin'})
            team.save()
            return HttpResponseRedirect(reverse('teams:list_teams'))
    else:
        form = TeamChangeForm()
    return render(request, 'teams/manage_team.html', {
        'form': form,
        'create': True,
    })


@login_and_team_required
def manage_team(request, team_slug):
    team = request.team
    if request.method == 'POST':
        form = TeamChangeForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('teams:list_teams'))
    else:
        form = TeamChangeForm(instance=team)
    return render(request, 'teams/manage_team.html', {
        'team': team,
        'form': form,
    })


def accept_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id)
    return render(request, 'teams/accept_invite.html', {
        'invitation': invitation,
    })


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get_queryset(self):
        # filter queryset based on logged in user
        return self.request.user.teams.all()

    def perform_create(self, serializer):
        # ensure logged in user is set on the model during creation
        team = serializer.save()
        team.members.add(self.request.user, through_defaults={'role': 'admin'})


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer

    def get_queryset(self):
        # filter queryset based on logged in user
        return self.queryset.filter(team__in=self.request.user.teams.all())

    def perform_create(self, serializer):
        # ensure logged in user is set on the model during creation
        invitation = serializer.save(invited_by=self.request.user)
        send_invitation(invitation)
