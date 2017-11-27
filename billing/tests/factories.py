import factory
from uuid import uuid4
from datetime import datetime, timedelta
from django.utils import timezone
from factory import fuzzy
from users.tests.factories import UserFactory
from billing.models import (Customer, Plan, Card,
                            Subscription, Event,
                            Invoice, InvoiceItem)


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    # Note that this is not actually a valid stripe id.
    # If you want a real stripe customer object, you should create a user factory,
    # and create it from there
    stripe_id = factory.Sequence(lambda n: "cus_%d" % n)
    created = fuzzy.FuzzyDateTime(start_dt=timezone.make_aware(datetime.now() - timedelta(days=7)))
    metadata = None
    livemode = False
    user = factory.SubFactory(UserFactory)
    account_balance = fuzzy.FuzzyInteger(low=-10000, high=10000)
    # For now
    currency = "usd"
    default_source = None


class PlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Plan

    stripe_id = factory.Sequence(lambda n: f"plan_{str(uuid4())[:16]}")
    created = fuzzy.FuzzyDateTime(start_dt=timezone.make_aware(datetime.now() - timedelta(days=7)))
    amount = fuzzy.FuzzyInteger(low=0, high=100000)
    currency = "usd"
    interval = fuzzy.FuzzyChoice([c[0] for c in Plan.INTERVAL_CHOICES])
    interval_count = 1
    name = fuzzy.FuzzyText(length=255)
    statement_descriptor = fuzzy.FuzzyText()
    trial_period_days = fuzzy.FuzzyInteger(low=0, high=90)


class CardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Card

    stripe_id = factory.Sequence(lambda n: "card_%d" % n)
    created = fuzzy.FuzzyDateTime(start_dt=timezone.make_aware(datetime.now() - timedelta(days=7)))
    metadata = None
    livemode = False

    customer = None
    # Note: This will clearly not generate valid addresses.
    # This should be used only for testing our own API, and not requests made to Stripe
    name = fuzzy.FuzzyText(length=200)
    address_city = fuzzy.FuzzyText(length=255)
    address_country = fuzzy.FuzzyText(length=255)
    address_line1 = fuzzy.FuzzyText(length=255)
    address_line1_check = fuzzy.FuzzyChoice([c[0] for c in Card.VERIFICATION_STATUS_CHOICES])
    address_line2 = fuzzy.FuzzyText(length=255)
    address_state = fuzzy.FuzzyText(length=100)
    address_zip = fuzzy.FuzzyText(length=25)
    address_zip_check = fuzzy.FuzzyChoice([c[0] for c in Card.VERIFICATION_STATUS_CHOICES])
    brand = fuzzy.FuzzyChoice([c[0] for c in Card.BRAND_CHOICES])
    cvc_check = fuzzy.FuzzyChoice([c[0] for c in Card.VERIFICATION_STATUS_CHOICES])
    last4 = fuzzy.FuzzyText(length=4)
    exp_month = fuzzy.FuzzyInteger(low=1, high=12)
    exp_year = fuzzy.FuzzyInteger(low=2018, high=2025)
    fingerprint = fuzzy.FuzzyText(length=100)
    funding = fuzzy.FuzzyChoice([c[0] for c in Card.FUNDING_CHOICES])


class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscription

    stripe_id = factory.Sequence(lambda n: "sub_%d" % n)
    created = fuzzy.FuzzyDateTime(start_dt=timezone.make_aware(datetime.now() - timedelta(days=7)))
    metadata = None
    livemode = False

    customer = None
    plan = factory.SubFactory(PlanFactory)
    application_fee_percent = fuzzy.FuzzyDecimal(low=0, high=1)
    cancel_at_period_end = fuzzy.FuzzyChoice([True, False])
    quantity = fuzzy.FuzzyInteger(low=1, high=5)
    status = fuzzy.FuzzyChoice([c[0] for c in Subscription.SUBSCRIPTION_STATUS_CHOICES])
    trial_start = timezone.make_aware(datetime.now())
    trial_end = factory.LazyAttribute(lambda obj: obj.trial_start + timedelta(days=obj.plan.trial_period_days))


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    stripe_id = factory.Sequence(lambda n: "evt_%d" % n)
    created = fuzzy.FuzzyDateTime(start_dt=timezone.make_aware(datetime.now() - timedelta(days=7)))
    metadata = None
    livemode = False
    api_version = fuzzy.FuzzyText(length=50)
    pending_webhooks = fuzzy.FuzzyInteger(low=0, high=5)
    request = fuzzy.FuzzyText(length=100)
    event_type = fuzzy.FuzzyChoice(["invoice.upcoming", "invoice.created", "invoice.payment_failed"])


class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invoice

    # Note that specifying none of these fields can currently create a lot of invalid
    # States relating to the period of billing, invoice amount, and payment status
    # If you want a valid invoice, you should specify all the relevant fields, or generate
    # One via subscription
    stripe_id = factory.Sequence(lambda n: "inv_%d" % n)
    created = fuzzy.FuzzyDateTime(start_dt=timezone.make_aware(datetime.now() - timedelta(days=7)))
    metadata = None
    livemode = False
    customer = factory.SubFactory(CustomerFactory)
    subscription = None
    amount_due = fuzzy.FuzzyInteger(low=100, high=5000)
    application_fee = fuzzy.FuzzyInteger(low=0, high=100)
    attempt_count = fuzzy.FuzzyInteger(low=0, high=3)
    attempted = fuzzy.FuzzyChoice([True, False])
    closed = fuzzy.FuzzyChoice([True, False])
    currency = "usd"
    invoice_date = fuzzy.FuzzyDateTime(start_dt=timezone.make_aware(datetime.now() - timedelta(days=365)))
    description = fuzzy.FuzzyText(length=100)
    next_payment_attempt = None
    paid = fuzzy.FuzzyChoice([True, False])
    period_start = fuzzy.FuzzyDateTime(start_dt=timezone.make_aware(datetime.now() - timedelta(days=365)))
    period_end = fuzzy.FuzzyDateTime(start_dt=timezone.make_aware(datetime.now() - timedelta(days=7)))
    reciept_number = fuzzy.FuzzyText(length=255)
    starting_balance = 0
    statement_descriptor = fuzzy.FuzzyText(length=100)
    subtotal = fuzzy.FuzzyInteger(low=100, high=4000)
    tax = fuzzy.FuzzyInteger(low=0, high=1000)
    total = fuzzy.FuzzyInteger(low=100, high=1000)


class InvoiceItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvoiceItem

    stripe_id = factory.Sequence(lambda n: "inv_item_%d" % n)
    created = fuzzy.FuzzyDateTime(start_dt=timezone.make_aware(datetime.now() - timedelta(days=7)))
    metadata = None
    livemode = False
    invoice = factory.SubFactory(InvoiceFactory)
    subscription = None
    amount = fuzzy.FuzzyInteger(low=100, high=1000)
    currency = "usd"
    invoice_date = fuzzy.FuzzyDateTime(start_dt=timezone.make_aware(datetime.now() - timedelta(days=365)))
    proration = fuzzy.FuzzyChoice([True, False])
    quantity = fuzzy.FuzzyInteger(low=1, high=5)
    description = fuzzy.FuzzyText(length=200)
