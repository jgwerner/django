from djstripe import webhooks as djstripe_hooks
from djstripe.models import Customer

from django.core.mail import mail_admins


@djstripe_hooks.handler('customer.subscription.deleted')
def email_admins_when_subscriptions_canceled(event, **kwargs):
    # example webhook handler to notify admins when a subscription is deleted/canceled
    try:
        customer_email = Customer.objects.get(id=event.data['object']['customer']).email
    except Customer.DoesNotExist:
        customer_email = 'unavailable'

    mail_admins(
        'Someone just canceled their subscription!',
        f'Their email was {customer_email}'
    )
