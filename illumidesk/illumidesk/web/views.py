from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


from illumidesk.teams.decorators import login_and_team_required
from illumidesk.teams.decorators import team_admin_required


def home(request):
    if request.user.is_authenticated:

        if request.user.teams.count():
            return HttpResponseRedirect(reverse('web:team_home', args=[request.user.teams.first().slug]))
        else:
            messages.info(request, _(
                'Teams are enabled but you have no teams. '
                'Create a team below to access the rest of the dashboard.'
            ))
            return HttpResponseRedirect(reverse('teams:manage_teams'))

    else:
        return render(request, 'web/landing_page.html')



@login_and_team_required
def team_home(request, team_slug):
    assert request.team.slug == team_slug
    return render(request, 'web/app_home.html', context={
        'team': request.team,
        'active_tab': 'dashboard',
    })


@team_admin_required
def team_admin_home(request, team_slug):
    assert request.team.slug == team_slug
    return render(request, 'web/team_admin.html', context={
        'active_tab': 'team-admin',
        'team': request.team,
    })

