import logging
import stripe
from django.conf import settings
from django.http import HttpResponse
log = logging.getLogger('billing')


def verify_signature(func):
    def wrapper(*args, **kwargs):
        log.info("Verifying signature for Stripe webhook.")
        request = args[0]
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRETS.get(func.__name__)

        try:
            stripe.Webhook.construct_event(payload,
                                           sig_header,
                                           endpoint_secret)
        except ValueError as e:
            # Invalid payload
            log.warning(f"Received an invalid webhook payload at {func.__name__}:")
            log.warning(f"Payload: {payload}\n Stacktrace:")
            log.exception(e)
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            log.warning(f"Received an invalid webhook signature at {func.__name__}:")
            log.warning(f"Signature: {sig_header}\n Stacktrace:")
            log.exception(e)
            return HttpResponse(status=400)
        return func(*args, **kwargs)
    return wrapper
