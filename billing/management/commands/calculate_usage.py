import django; django.setup()
import logging
from datetime import datetime
from django.core.management import BaseCommand
from billing.tbs_utils import (calculate_usage_for_period,
                               shutdown_servers_for_free_users)
log = logging.getLogger('billing')


class Command(BaseCommand):
    help = "Calculate server usage"

    def handle(self, *args, **options):
        self.stdout.write("Calculating usage...")

        beginning = datetime.now()

        log.info(f"calculate_usage.py invoked at {beginning}")
        usage_map = calculate_usage_for_period()
        calc_finished = datetime.now()

        log.info(f"calculate_usage_for_period() returned at: {calc_finished}")
        calc_duration = (calc_finished - beginning).total_seconds()
        log.info(f"Total seconds spent there: {calc_duration}")

        self.stdout.write("Finished calculating usage. Will now shut down any necessary servers.")

        shutdown_start = datetime.now()
        log.info(f"Shutting down servers at {shutdown_start}")
        shutdown_servers_for_free_users(usage_map)

        self.stdout.write("Completed shutting down servers.")

        finished = datetime.now()
        shutdown_time = (finished - shutdown_start).total_seconds()
        log.info(f"Time spent shutting down: {shutdown_time}")

        total_time = calc_duration + shutdown_time
        log.info(f"Total time spent in calculate usage.py: {total_time}")
        self.stdout.write("All operations completed.")
