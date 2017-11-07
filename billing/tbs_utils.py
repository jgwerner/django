import logging
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from billing.models import Invoice
from servers.models import ServerRunStatistics
from notifications.utils import create_notification
log = logging.getLogger('servers')


def calculate_usage_for_current_billing_period() -> None:
    log.debug("In calculate usage method")
    # TODO: In theory there is only one open invoice per user, but this needs to be verified, especially for teams
    # Do select related for user and plan
    invoices = Invoice.objects.filter(closed=False).select_related('customer__user',
                                                                   'subscription__plan')
    log.debug(("inv count", invoices.count()))
    user_runs_mapping = {}
    for inv in invoices:
        user = inv.customer.user
        runs = ServerRunStatistics.objects.filter(Q(stop=None) | Q(start__gte=inv.period_start),
                                                  owner=inv.customer.user)
        log.debug(("server runs count", runs.count()))
        # Not sure this will be needed after all
        user_runs_mapping[user] = runs

        # TODO: This is a very slow way of doing this calculation. Only using it now for clarity's sake.
        # TODO: Will refactor soon for performance.
        this_user_total = 0.0
        for run in runs:
            log.debug(("run vars", run.start, run.stop, run.duration))
            # Server Memory GB * Duration of run in hours = usage
            if run.start < inv.period_start:
                run_duration = ((run.stop or timezone.now()) - inv.period_start).seconds
            else:
                if run.duration is None:
                    run.duration = run.stop - run.start
                    run.save()
                run_duration = run.duration.seconds

            log.debug(("run duration", run_duration))
            this_run_gb_hours = (run.server_size_memory / 1024) * (run_duration / 3600)
            this_user_total += this_run_gb_hours

        # Now check if user has exceeded a certain threshold of usage (e.g. 75%, 90%, etc.) and
        # send notification accordingly.

        # TODO: Agree on what this field in the plan's metadata should be called
        log.debug(("this user total", this_user_total))
        usage_percent = (this_user_total / inv.subscription.plan.metadata.get('gb_hours')) * 100
        log.debug(("usage percent", usage_percent))
        if usage_percent > settings.USAGE_WARNING_THRESHOLD:
            log.info(f"User {user} has used {usage_percent}% of their plan. Sending a notification.")
            create_notification(user=user,
                                actor=inv,
                                target=None,
                                entity="billing",
                                notif_type="usage_warning")
