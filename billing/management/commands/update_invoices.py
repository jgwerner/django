import django; django.setup()
from django.core.management import BaseCommand
from billing.tbs_utils import update_invoices_with_usage
from servers.models import Server
from servers.tasks import stop_server


class Command(BaseCommand):
    help = "Calculate server usage"

    def handle(self, *args, **options):
        print("Updating invoices within the next 30 minutes...")
        usage_map = update_invoices_with_usage()
        shutdown_users = [pk for pk, bill_data in usage_map.items() if bill_data.stop_all_servers]
        # Something about this query makes me feel like it might be incorrect
        # TODO: Write a unit test for this
        servers_to_stop = Server.objects.filter(project__collaborator__user__pk__in=[shutdown_users],
                                                project__collaborator__owner=True)
        for server in servers_to_stop:
            stop_server.apply_async(server)
