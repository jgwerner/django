from djstripe.enums import SubscriptionStatus
from djstripe.models import Subscription
from djstripe.utils import CURRENCY_SIGILS

from django.utils.functional import cached_property


class SubscriptionModelMixin:
    """
    Helper class to be used with Stripe Subscriptions.

    Assumes that the associated subclass is a django model containing at least a
    subscription field that is a ForeignKey to a djstripe.Subscription object.

    Optionally, the subclass can also contain a customer field which is a djstripe.Customer.
    """
    # subclass should override with appropriate foreign keys as needed
    subscription = None
    customer = None

    @cached_property
    def stripe_subscription(self):
        return self._get_stripe_subscription()

    @cached_property
    def active_stripe_subscription(self):
        return self._get_stripe_subscription(only_include_active=True)

    def clear_subscription_caches(self):
        del self.stripe_subscription
        del self.active_stripe_subscription

    def _get_stripe_subscription(self, only_include_active=False):
        # if they have an associated subscription object that matches, use it
        if (self.subscription and
                (not only_include_active or
                 (only_include_active and self.subscription.status == SubscriptionStatus.active))):
            return self.subscription
        if not self.customer:
            return None
        else:
            # else fall back to pulling subscription details out of the associated customer object
            query_args = dict(status=SubscriptionStatus.active) if only_include_active else {}
            try:
                return self.customer.subscriptions.get(
                    **query_args
                )
            except Subscription.DoesNotExist:
                return None
            except Subscription.MultipleObjectsReturned as e:
                # this is unexpected so log it
                # todo: add sentry/error capture support back in
                # capture_exception(e)
                # but also fail gracefully
                return self.customer.subscriptions.filter(
                    status=SubscriptionStatus.active
                ).first()

    def has_active_subscription(self):
        return self.active_stripe_subscription is not None

    def has_subscription(self):
        return self.stripe_subscription is not None


def get_friendly_currency_amount(amount, currency):
    # modified from djstripe's version to only include sigil or currency, but not both
    currency = currency.upper()
    sigil = CURRENCY_SIGILS.get(currency, "")
    if sigil:
        return "{sigil}{amount:.2f}".format(sigil=sigil, amount=amount)
    else:
        return "{amount:.2f} {currency}".format(amount=amount, currency=currency)
