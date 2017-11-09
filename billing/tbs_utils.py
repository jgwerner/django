import logging
from django.conf import settings
from django.db.models import (Q, Sum, F, DurationField,
                              Case, When, ExpressionWrapper)
from django.db.models.functions import Greatest
from django.utils import timezone
from billing.models import Invoice
from servers.models import ServerRunStatistics
from notifications.utils import create_notification
log = logging.getLogger('servers')


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

        user_runs = ServerRunStatistics.objects.filter(Q(stop=None) | Q(start__gte=inv.period_start),
                                                       owner=inv.customer.user)
        usage_in_mb_seconds = user_runs.aggregate(usage=Sum(Case(When(duration__isnull=False,
                                                                      then=ExpressionWrapper((F('stop') - Greatest(
                                                                          F('start'), inv.period_start)) * F(
                                                                          'server_size_memory'),
                                                                                             output_field=DurationField())),
                                                                 When(duration__isnull=True,
                                                                      then=ExpressionWrapper((timezone.now() - Greatest(
                                                                          F('start'), inv.period_start)) * F(
                                                                          'server_size_memory'),
                                                                                             output_field=DurationField())
                                                                      )
                                                                 ),
                                                            output_field=DurationField()))['usage'].total_seconds()

        usage_in_gb_hours = usage_in_mb_seconds / 1024 / 3600
        usage_percent = (usage_in_gb_hours / inv.subscription.plan.metadata.get('gb_hours')) * 100
        user_runs_mapping[user.pk] = usage_percent

        if usage_percent > settings.USAGE_WARNING_THRESHOLD:
            log.info(f"User {user} has used {usage_percent}% of their plan. Sending a notification.")
            create_notification(user=user,
                                actor=inv,
                                target=None,
                                entity="billing",
                                notif_type="usage_warning")
    return user_runs_mapping
