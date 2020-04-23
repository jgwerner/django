from django import template
from django.templatetags.static import static

from illumidesk.meta import absolute_url
from illumidesk.teams.roles import user_can_access_team
from illumidesk.teams.roles import user_can_administer_team


register = template.Library()


@register.filter
def get_title(project_meta, page_title=None):
    if page_title:
        return '{} | {}'.format(page_title, project_meta['NAME'])
    else:
        return project_meta['TITLE']


@register.filter
def get_description(project_meta, page_description=None):
    return page_description or project_meta['DESCRIPTION']


@register.filter
def get_image_url(project_meta, page_image=None):
    if page_image and page_image.startswith('/'):
        page_image = absolute_url(static(page_image))
    return page_image or project_meta['IMAGE']


@register.filter
def is_member_of(user, team):
    return user_can_access_team(user, team)


@register.filter
def is_admin_of(user, team):
    return user_can_administer_team(user, team)
