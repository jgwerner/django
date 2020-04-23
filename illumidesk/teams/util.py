from illumidesk.teams.models import Team
from illumidesk.utils.slug import get_next_unique_slug


def get_next_unique_team_slug(team_name):
    """
    Gets the next unique slug based on the name. Appends -1, -2, etc. until it finds
    a unique value.
    :param team_name:
    :return:
    """
    return get_next_unique_slug(Team, team_name, 'slug')
