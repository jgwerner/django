import django; django.setup() # noqa
import logging
from datetime import datetime
from django.core.management import BaseCommand
from billing.tbs_utils import (update_invoices_with_usage,
                               shutdown_servers_for_free_users)
log = logging.getLogger('billing')


class Command(BaseCommand):
    help = "Calculate server usage"

    def handle(self, *args, **options):
        self.stdout.write("Updating invoices that close within the next 30 minutes...")

        beginning = datetime.now()

        log.info(f"update_invoices.py invoked at {beginning}")
        usage_map = update_invoices_with_usage()
        calc_finished = datetime.now()

        log.info(f"update_invoices_with_usage() returned at: {calc_finished}")
        calc_duration = (calc_finished - beginning).total_seconds()

        self.stdout.write("Finished calculating usage and updating invoices. "
                          "Will now shut down any necessary servers.")

        log.info(f"Total seconds spent there: {calc_duration}")

        shutdown_start = datetime.now()
        log.info(f"Shutting down servers at {shutdown_start}")
        shutdown_servers_for_free_users(usage_map)

        self.stdout.write("Completed shutting down servers.")

        finished = datetime.now()
        shutdown_time = (finished - shutdown_start).total_seconds()
        log.info(f"Time spent shutting down: {shutdown_time}")

        total_time = calc_duration + shutdown_time
        log.info(f"Total time spent in update_invoices.py: {total_time}")

        self.stdout.write("All operations completed.")
