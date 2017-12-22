import logging
import stripe
from billing.models import Subscription
log = logging.getLogger('billing')


def mock_subscription_retrieve(subscription: Subscription) -> dict:
    retdict = {}

    non_relational = [f for f in Subscription._meta.get_fields() if not f.is_relation]
    relational = [f for f in  Subscription._meta.get_fields() if f.is_relation and f.related_model == Subscription]

    for field in non_relational:
        if field.name != "id":
            retdict[field.name] = getattr(subscription, field.name)

    for field in relational:
        log.debug((field.name, field.related_model, field.model))
        retdict[field.name] = getattr(subscription, field.name).stripe_id
    return retdict


def signature_verification_error():
    return stripe.error.SignatureVerificationError("foo", "bar")
