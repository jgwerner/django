from django import template

from illumidesk.teams.roles import user_can_access_team
from illumidesk.teams.roles import user_can_administer_team


register = template.Library()


@register.filter
def is_member_of(user, team):
    return user_can_access_team(user, team)


@register.filter
def is_admin_of(user, team):
    return user_can_administer_team(user, team)
