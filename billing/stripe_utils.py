import logging
from typing import List
from datetime import datetime
from decimal import getcontext
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from users.models import User

from billing.models import (Customer, Invoice,
                            Plan, Subscription,
                            Card, Event, InvoiceItem)
log = logging.getLogger('billing')

if settings.MOCK_STRIPE:
    from billing.tests import mock_stripe as stripe
    log.info("Importing mock stripe in stripe utils.")
else:
    import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY
getcontext().prec = 6


def handle_foreign_key_field(stripe_data, stripe_field, model_field):
    init_value = stripe_data[stripe_field]
    final_value = None
    identifier = None

    if init_value is not None:
        if isinstance(init_value, dict):
            identifier = init_value.get("id")

        elif isinstance(init_value, model_field.related_model):
            final_value = init_value

        else:
            identifier = init_value

        if hasattr(model_field.related_model, "stripe_id"):
            kwargs = {'stripe_id': identifier}
        elif final_value is None:
            kwargs = {'pk': identifier}

        if final_value is None:
            final_value = model_field.related_model.objects.filter(**kwargs).first()

    return final_value


def convert_field_to_stripe(model, stripe_field, stripe_data):
    field_name = "stripe_id" if stripe_field == "id" else stripe_field
    value = stripe_data[stripe_field]

    all_model_field_names = [f.name for f in model._meta.get_fields()]
    if field_name in all_model_field_names:  # or field_name.replace("_id", "") in all_model_field_names:
        model_field = model._meta.get_field(field_name)
    else:
        model_field = field_name = value = None

    # Not sure how to handle many to many fields just yet. Not sure we will have to.
    # I've really come to hate this following block.
    # Will have to think about how to clean it up.
    # I'm guessing it's also not very performant
    if (model_field is not None and
            (model_field.is_relation and not model_field.many_to_many)):

        value = handle_foreign_key_field(stripe_data,
                                         stripe_field,
                                         model_field)

    elif isinstance(model_field, models.DateTimeField):
        if value is not None:
            if not isinstance(value, datetime):
                value = datetime.fromtimestamp(value)
                value = timezone.make_aware(value)

    return (field_name, value)


def convert_stripe_object(model, stripe_obj):
    dict_tuples = [convert_field_to_stripe(model, field, stripe_obj)
                   for field in stripe_obj]
    converted = dict(tup for tup in dict_tuples if tup[0] is not None)
    if "created" not in converted:
        converted['created'] = timezone.make_aware(datetime.now())
    return converted


def create_stripe_customer_from_user(auth_user: User) -> Customer:
    stripe_response = stripe.Customer.create(description=auth_user.first_name + " " + auth_user.last_name,
                                             email=auth_user.email)

    converted_data = convert_stripe_object(Customer, stripe_response)
    customer, created = Customer.objects.get_or_create(user=auth_user,
                                                       defaults=converted_data)

    if created:
        log.info(f"Successfully reated new customer for {auth_user.username}")

    return customer


def update_plan_in_stripe(data: dict):
    stripe_id = data.pop("id")
    stripe_obj = stripe.Plan.retrieve(stripe_id)
    for attr, val in data.items():
        setattr(stripe_obj, attr, val)
    stripe_obj.save()


def create_plan_in_stripe(validated_data):
    plan_stripe_id = validated_data.get('name').lower().replace(" ", "-")
    try:
        stripe_plan = stripe.Plan.retrieve(plan_stripe_id)
        plan = Plan.objects.get(stripe_id=plan_stripe_id)
    except stripe.error.InvalidRequestError:
        # Plan doesn't exist in Stripe. This is the expected flow.
        log.info(f"Plan f{validated_data.get('name')} did not exist in Stripe. Creating it.")
        stripe_response = stripe.Plan.create(id=validated_data.get('name').lower().replace(" ", "-"),
                                             amount=validated_data.get('amount'),
                                             currency=validated_data.get('currency'),
                                             interval=validated_data.get('interval'),
                                             interval_count=validated_data.get('interval_count'),
                                             name=validated_data.get('name'),
                                             statement_descriptor=validated_data.get('statement_descriptor'),
                                             trial_period_days=validated_data.get('trial_period_days'))

        converted_data = convert_stripe_object(Plan, stripe_response)
        plan = Plan(**converted_data)
    except ObjectDoesNotExist:
        log.warning(f"Plan {plan_stripe_id} exists in stripe, but not in the local database. Creating it there.")
        converted_data = convert_stripe_object(Plan, stripe_plan)
        plan = Plan(**converted_data)
    else:
        log.info(f"Plan {plan_stripe_id} already existed in both Stripe and the local database. Hmm.")

    return plan


def create_subscription_in_stripe(validated_data, user=None):
    customer = validated_data.get("customer")
    if customer is None and user is None:
        raise ValueError("Validated_data must contain 'user', or the user object"
                         "must be passed as a kwarg.")
    if customer is None:
        customer = user.customer

    plan_id = validated_data.get("plan")

    if isinstance(plan_id, Plan):
        plan = plan_id
    else:
        plan = Plan.objects.get(pk=plan_id)

    stripe_response = stripe.Subscription.create(customer=customer.stripe_id,
                                                 plan=plan.stripe_id)
    converted_data = convert_stripe_object(Subscription, stripe_response)
    return Subscription.objects.create(**converted_data)


def create_card_in_stripe(validated_data, user=None):
    user_pk = validated_data.get("user")
    if user is None and user_pk is None:
        raise ValueError("Validated_data must contain 'user', or the user object"
                         " must be passed as a kwarg.")
    if user is None:
        customer = Customer.objects.get(user__pk=user_pk)
    else:
        customer = user.customer

    stripe_cust = stripe.Customer.retrieve(customer.stripe_id)

    token = validated_data.get("token")
    if token is None:
        validated_data['object'] = "card"
        stripe_resp = stripe_cust.sources.create(source=validated_data)
    else:
        stripe_resp = stripe_cust.sources.create(source=token)

    stripe_resp['customer'] = customer.stripe_id

    converted_data = convert_stripe_object(Card, stripe_resp)
    return Card.objects.create(**converted_data)


def create_event_from_webhook(stripe_obj):
    event = Event.objects.filter(stripe_id=stripe_obj['id']).first()
    if not event:
        # This conversion is *just* custom enough that using the convert method isn't useful
        create_ts = datetime.fromtimestamp(stripe_obj['created'])
        create_ts = timezone.make_aware(create_ts)
        event_parms = {'stripe_id': stripe_obj['id'],
                       'created': create_ts,
                       'livemode': stripe_obj['livemode'],
                       'api_version': stripe_obj['api_version'],
                       'event_type': stripe_obj['type']}
        event = Event(**event_parms)
        event.save()
        log.info("Created new stripe event: {event}:{type}".format(event=event.stripe_id,
                                                                   type=event.event_type))
        return event
    log.info("Event {event}:{type} already exists. Doing nothing.".format(event=stripe_obj['id'],
                                                                          type=stripe_obj['type']))
    return None


def find_or_create_invoice(stripe_data):
    stripe_data['invoice_date'] = stripe_data['date']
    converted = convert_stripe_object(Invoice, stripe_data)
    invoice, created = Invoice.objects.update_or_create(stripe_id=converted['stripe_id'],
                                                        defaults=converted)
    if created:
        log.info("Created a new invoice: {invoice}".format(invoice=invoice.pk))
    else:
        log.info("Updated an invoice: {invoice}".format(invoice=invoice.stripe_id))
    return invoice


def handle_stripe_invoice_payment_status_change(stripe_obj):
    signal_data = {}
    event = create_event_from_webhook(stripe_obj)

    if event is not None:
        sub_stripe_id = stripe_obj['data']['object']['subscription']
        stripe_subscription = stripe.Subscription.retrieve(sub_stripe_id)
        converted_data = convert_stripe_object(Subscription, stripe_subscription)
        subscription = Subscription.objects.get(stripe_id=sub_stripe_id)

        stripe_data = stripe_obj['data']['object']
        invoice = find_or_create_invoice(stripe_data)

        if event.event_type == "invoice.payment_succeeded" or (event.event_type == "invoice.payment_failed" and
                                                               subscription.metadata and subscription.metadata.get('has_been_active')):
            log.info(f"Subscription {subscription} has been active before and payment failed (or this was a successful "
                     f"payment. Generating a notification.")
            signal_data = {'user': subscription.customer.user,
                           'actor': subscription,
                           'target': invoice,
                           'notif_type': event.event_type}
        else:
            log.info(f"Subscription {subscription} has NOT been active before, meaning it was in trial status "
                     f"before payment failure. Not generating a notification.")

        for key in converted_data:
            if key not in ["customer", "plan", "metadata"]:
                setattr(subscription, key, converted_data[key])
        if subscription.status == Subscription.ACTIVE:
            if subscription.metadata is None:
                subscription.metadata = {}
            subscription.metadata.update({'has_been_active': True})
            log.info(f"Subscription {subscription} has status active. Marking it as such in metadata "
                     f"for notification purposes.")
        subscription.save()
        log.info(f"Updated subscription {subscription} after {event.event_type}.")

    return signal_data


def handle_stripe_invoice_created(stripe_obj):
    """
    :param stripe_obj: The Stripe *event* object
    :return: None
    """
    event = create_event_from_webhook(stripe_obj)
    if event is not None:
        stripe_invoice = stripe_obj['data']['object']
        find_or_create_invoice(stripe_invoice)


def create_invoice_item_for_compute_usage(customer_stripe_id, usage_data):
    stripe_invoice_item = stripe.InvoiceItem.create(customer=customer_stripe_id,
                                                    amount=int(usage_data['total']),
                                                    currency="usd",
                                                    description="3Blades Compute Usage")
    converted_data = convert_stripe_object(InvoiceItem, stripe_invoice_item)
    converted_data['quantity'] = 1
    return InvoiceItem.objects.create(**converted_data)


def add_buckets_to_stripe_invoice(customer_stripe_id: str, buckets: int) -> InvoiceItem:
    amount = buckets * (settings.BUCKET_COST_USD * 100)
    stripe_invoice_item = stripe.InvoiceItem.create(customer=customer_stripe_id,
                                                    amount=amount,
                                                    currency="usd",
                                                    description="3Blades Compute Usage")
    converted_data = convert_stripe_object(InvoiceItem, stripe_invoice_item)
    converted_data['quantity'] = 1
    return InvoiceItem.objects.create(**converted_data)


def assign_customer_to_default_plan(customer: Customer):
    existing_sub = Subscription.objects.filter(customer=customer)
    if not existing_sub.exists():
        log.info(f"Creating subscription to default plan for {customer.user.username}.")
        default_plan = Plan.objects.filter(stripe_id=settings.DEFAULT_STRIPE_PLAN_ID).first()
        if not default_plan:
            log.error(f"Selected default plan {settings.DEFAULT_STRIPE_PLAN_ID} does not exist in DB. "
                      f"Make sure this setting is correct, and that everything is synchronized with Stripe!")
            free_plan_data = {'name': settings.DEFAULT_STRIPE_PLAN_ID.replace("-", " ").title(),
                              'amount': 0,
                              'currency': "usd",
                              'interval': "month",
                              'interval_count': 1,
                              'trial_period_days': 14,
                              'metadata': {"gb_hours": 10}}
            try:
                log.warning("Since the default plan did not exist in the DB, the system will now add the "
                            "user to a free plan to avoid failure.")
                log.info("First make sure it doesn't exist in Stripe already...")
                stripe_resp = stripe.Plan.retrieve(settings.DEFAULT_STRIPE_PLAN_ID)
                free_plan_data['created'] = timezone.now()
                default_plan, created = Plan.objects.get_or_create(stripe_id=stripe_resp['id'],
                                                                   defaults=free_plan_data)

                if created:
                    log.info("Free plan existed in Stripe, but not the local database, so it "
                             " was created.")
            except stripe.error.InvalidRequestError:
                log.info("Free plan did NOT exist in Stripe...creating it there and in local database.")
                default_plan = create_plan_in_stripe(free_plan_data)
                default_plan.save()
        sub_data = {'customer': customer,
                    'plan': default_plan}
        create_subscription_in_stripe(sub_data)
        log.info("Finished creating default subscription.")


def handle_subscription_updated(stripe_event):
    if stripe_event['type'] != "customer.subscription.updated":
        raise ValueError(f"This function only handles subscription.updated events (specifically trail expiry). "
                         f"You passed {stripe_event['type']}")
    signal_data = {}
    stripe_sub = stripe_event['data']['object']
    subscription = Subscription.objects.filter(stripe_id=stripe_sub['id']).first()

    if subscription is None:
        log.error("Received a subscription updated webhook for a subscription that does not exist in the database."
                  "As much information as possible will be logged, but the event will NOT be entered in the DB so "
                  "that it will still be processed if Stripe sends the event again.")
        log.error(f"Data sent from Stripe: {stripe_event}")

    else:
        create_event_from_webhook(stripe_event)
        if (subscription.status in [Subscription.TRIAL, Subscription.ACTIVE]
            and stripe_sub['status'] in [Subscription.PAST, Subscription.UNPAID, Subscription.CANCELED]):
            signal_data = {'user': subscription.customer.user,
                           'actor': subscription.customer.user,
                           'target': subscription,
                           'notif_type': "subscription.trial_ended"}
        converted_data = convert_stripe_object(Subscription, stripe_sub)
        for key in converted_data:
            if key not in ["customer", "plan", "metadata"]:
                setattr(subscription, key, converted_data[key])
        if subscription.status == Subscription.ACTIVE:
            if subscription.metadata is None:
                subscription.metadata = {}
            subscription.metadata.update({'has_been_active': True})
            log.info(f"Subscription {subscription} has status active. Marking it as such in metadata "
                     f"for notification purposes.")
        subscription.save()

    return signal_data


def cancel_subscriptions(subscription_ids: List[str]) -> None:
    subscriptions = Subscription.objects.filter(id__in=subscription_ids,
                                                status__in=[Subscription.ACTIVE, Subscription.TRIAL])
    for sub in subscriptions:
        stripe_obj = stripe.Subscription.retrieve(sub.stripe_id)
        stripe_response = stripe_obj.delete()
        log.debug((f"Stripe resp status", stripe_response['status']))
        sub.delete(new_status=stripe_response['status'])
        log.info(f"Canceled subscription {sub.pk}.")
