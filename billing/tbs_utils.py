import logging
from decimal import Decimal, getcontext
from django.conf import settings
from django.db.models import (Q, Sum, F, DurationField,
                              Case, When, ExpressionWrapper)
from django.db.models.functions import Greatest
from django.utils import timezone
from billing.models import Invoice
from servers.models import ServerRunStatistics
from notifications.utils import create_notification
log = logging.getLogger('servers')
getcontext().prec = 6


def calculate_usage_for_current_billing_period() -> dict:
    """
    :return: user_runs_mapping is a dict that maps user.pk -> 
             Percentage of plan used for this billing period. 
    """
    # TODO: In theory there is only one open invoice per user, but this needs to be verified, especially for teams
    # Do select related for user and plan
    invoices = Invoice.objects.filter(closed=False).select_related('customer__user',
                                                                   'subscription__plan')
    user_runs_mapping = {}
    for inv in invoices:
        user = inv.customer.user

        if user.pk in user_runs_mapping:
            # TODO: Decide what to do in this scenario
            log.warning(f"For some reason {user} currently has multiple open invoices. "
                        f"This shouldn't really happen, and I'm not sure how to handle it for now.")

        """ 
            The complicated Django query that follows is necessary for performance reasons.
            For the sake of clarity, here is a python-only implementation:
            runs = ServerRunStatistics.objects.filter(Q(stop=None) | Q(start__gte=inv.period_start),
                                                  owner=inv.customer.user)
            this_user_total = 0.0
            for run in runs:
                # If a run has not been stopped yet, use timezone.now() as the cutoff
                # If a run started before the current billing period, use inv.period_start as the beginning,
                # as we only want to bill for usage that has occurred in this period.
                run_duration = ((run.stop or timezone.now()) - max(inv.period_start, run.start)).total_seconds()
    
                # server_size_memory is in megabytes, so divide to get GB
                # run_duration is in seconds, so divide to get hours
                this_run_gb_hours = (run.server_size_memory / 1024) * (run_duration / 3600)
                this_user_total += this_run_gb_hours
        """

        user_runs = ServerRunStatistics.objects.filter(Q(stop=None) | Q(stop__gte=inv.period_start),
                                                       owner=inv.customer.user)
        usage_in_mb_seconds = user_runs.aggregate(usage=Sum(Case(When(stop__isnull=False,
                                                                      then=ExpressionWrapper((F('stop') - Greatest(
                                                                          F('start'), inv.period_start)) * F(
                                                                          'server_size_memory'),
                                                                                             output_field=DurationField())),
                                                                 When(stop__isnull=True,
                                                                      then=ExpressionWrapper((timezone.now() - Greatest(
                                                                          F('start'), inv.period_start)) * F(
                                                                          'server_size_memory'),
                                                                                             output_field=DurationField())
                                                                      )
                                                                 ),
                                                            output_field=DurationField()))['usage']
        if usage_in_mb_seconds is not None:
            usage_in_mb_seconds = Decimal(usage_in_mb_seconds.total_seconds())
            # Divide by 1024 to get gigabytes, then 3600 to get hours. MB Seconds -> GB Hours
            usage_in_gb_hours = usage_in_mb_seconds / 1024 / 3600
            usage_percent = (usage_in_gb_hours / inv.subscription.plan.metadata.get('gb_hours')) * 100
            user_runs_mapping[user.pk] = usage_percent

            # TODO: Refactor this to use a bulk create somehow. This adds a ton of overhead
            if usage_percent > settings.USAGE_WARNING_THRESHOLD:
                log.info(f"User {user} has used {usage_percent}% of their plan. Sending a notification.")
                create_notification(user=user,
                                    actor=inv,
                                    target=None,
                                    entity="billing",
                                    notif_type="usage_warning")
    return user_runs_mapping
