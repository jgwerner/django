from datetime import datetime
from django.db.models import Sum, Max, F, Count
from django.db.models.functions import Coalesce, Now, Greatest
from projects.models import Project
from servers.models import ServerRunStatistics, Server
from servers.tasks import stop_server


def get_server_usage(server_ids, begin_measure_time=None):
    """
    :param server_ids: List of server pks that you want run statistics for.
    :param begin_measure_time: A datetime.datetime instance that the statistics should start from.
                               Usually for billing purposes.
    :return: A Django aggregate queryset
    """
    if begin_measure_time is None:
        # Since this is the beginning of epoch time, we're basically doing max(ServerRunStatistics.start, 0)
        begin_measure_time = datetime(year=1970, month=1, day=1)

    servers = ServerRunStatistics.objects.filter(server__in=Server.objects.tbs_filter(server_ids))
    usage_data = servers.aggregate(duration=Sum(Coalesce(F('stop'), Now()) - Greatest('start', begin_measure_time)),
                                   runs=Count('id'),
                                   start=Max('start'),
                                   stop=Max('stop'))
    return usage_data


def is_server_token(token):
    return Server.objects.filter(access_token=token).exists()


def stop_all_servers_for_project(project: Project):
    servers = Server.objects.filter(project=project)
    for server in servers:
        stop_server(server)
