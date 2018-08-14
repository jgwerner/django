from django.contrib.postgres.fields import JSONField
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from base.models import TBSQuerySet


class BillingAddress(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state_province = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=11)
    created_at = models.DateTimeField(auto_now_add=True)


class StripeModel(models.Model):
    stripe_id = models.TextField(unique=True)
    created = models.DateTimeField()
    metadata = JSONField(null=True)
    livemode = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Event(StripeModel):
    api_version = models.CharField(max_length=50)
    data = JSONField(null=True)
    pending_webhooks = models.PositiveIntegerField(default=0)
    request = models.CharField(max_length=100)
    event_type = models.CharField(max_length=255)


class Customer(StripeModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    # Should account_balance really be exposed?
    account_balance = models.IntegerField(default=0)
    currency = models.CharField(max_length=10, null=True)
    default_source = models.ForeignKey("Card", null=True, related_name="+", on_delete=models.CASCADE)
    last_invoice_sync = models.DateTimeField(null=True)

    def has_active_subscription(self):
        has_sub = self.subscription_set.filter(status__in=[Subscription.TRIAL,
                                                           Subscription.ACTIVE]).exists()
        return has_sub

    @property
    def current_invoice(self):
        try:
            invoice = self.invoice_set.get(closed=False)
        except Invoice.DoesNotExist:
            invoice = None
        return invoice

    @property
    def namespace_name(self):
        return self.user.username

    def get_absolute_url(self, version):
        return reverse('customer-detail', kwargs={
            'namespace': self.namespace_name, 'version': version, 'pk': str(self.pk)})


class Card(StripeModel):
    customer = models.ForeignKey(Customer)
    name = models.CharField(max_length=200, null=True)
    address_city = models.CharField(max_length=255, null=True)
    address_country = models.CharField(max_length=255, null=True)
    address_line1 = models.CharField(max_length=255, null=True)

    PASS = "pass"
    FAIL = "fail"
    UNAVAILABLE = "unavailable"
    UNCHECKED = "unchecked"

    VERIFICATION_STATUS_CHOICES = ((PASS, "Passed"),
                                   (FAIL, "Failed"),
                                   (UNAVAILABLE, "Unavailable"),
                                   (UNCHECKED, "Unchecked"))

    address_line1_check = models.CharField(max_length=12, choices=VERIFICATION_STATUS_CHOICES, null=True)
    address_line2 = models.CharField(max_length=255, null=True)
    address_state = models.CharField(max_length=100, null=True)
    address_zip = models.CharField(max_length=25, null=True)
    address_zip_check = models.CharField(max_length=12, choices=VERIFICATION_STATUS_CHOICES, null=True)

    VISA = "Visa"
    AMEX = "American Express"
    MASTER = "MasterCard"
    DISC = "Discover"
    JCB = "JCB"
    DINER = "Diners Club"
    UNKNOWN = "Unknown"

    BRAND_CHOICES = ((VISA, VISA),
                     (AMEX, AMEX),
                     (MASTER, MASTER),
                     (DISC, DISC),
                     (JCB, JCB),
                     (DINER, DINER),
                     (UNKNOWN, UNKNOWN))
    brand = models.CharField(max_length=16, choices=BRAND_CHOICES)
    cvc_check = models.CharField(max_length=12, choices=VERIFICATION_STATUS_CHOICES, null=True)
    # Tokenized numbers only
    dynamic_last4 = models.CharField(max_length=4, null=True)
    # Non-Tokenized
    last4 = models.CharField(max_length=4)
    exp_month = models.IntegerField()
    exp_year = models.IntegerField()
    fingerprint = models.TextField()

    CREDIT = "Credit"
    DEBIT = "Debit"
    PRE = "Prepaid"

    FUNDING_CHOICES = ((CREDIT, CREDIT),
                       (DEBIT, DEBIT),
                       (PRE, PRE),
                       (UNKNOWN, UNKNOWN))

    funding = models.CharField(max_length=7, choices=FUNDING_CHOICES)

    @property
    def namespace_name(self):
        return self.customer.namespace_name

    def get_absolute_url(self, version):
        return reverse('card-detail', kwargs={'namespace': self.namespace_name, 'version': version, 'pk': str(self.pk)})


class Plan(StripeModel):
    amount = models.PositiveIntegerField(help_text="Amount, in cents (or equivalent) the plan should cost."
                                                   " For example, a value of 500 -> $5.00")
    currency = models.CharField(max_length=3, default="usd")

    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

    INTERVAL_CHOICES = [(DAY, "Day"),
                        (WEEK, "Week"),
                        (MONTH, "Month"),
                        (YEAR, "Year")]

    interval = models.CharField(max_length=5, choices=INTERVAL_CHOICES)
    interval_count = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    statement_descriptor = models.TextField(null=True)
    trial_period_days = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.name

    @property
    def namespace_name(self):
        return self.subscription_set.first().namespace_name

    def get_absolute_url(self, version):
        return reverse('card-detail', kwargs={'namespace': self.namespace_name, 'version': version, 'pk': str(self.pk)})


class SubscriptionQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        user = namespace.object if namespace.type == 'user' else namespace.object.owner
        return self.filter(customer__user=user)


class Subscription(StripeModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    application_fee_percent = models.DecimalField(decimal_places=2, max_digits=3, null=True)
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True)
    current_period_start = models.DateTimeField(null=True)
    current_period_end = models.DateTimeField(null=True)
    start = models.DateTimeField(null=True)
    ended_at = models.DateTimeField(null=True)
    quantity = models.PositiveIntegerField()

    TRIAL = "trialing"
    ACTIVE = "active"
    PAST = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"

    SUBSCRIPTION_STATUS_CHOICES = [(TRIAL, "Trial"),
                                   (ACTIVE, "Active"),
                                   (PAST, "Past Due"),
                                   (CANCELED, "Canceled"),
                                   (UNPAID, "Unpaid")]
    status = models.CharField(max_length=8, choices=SUBSCRIPTION_STATUS_CHOICES)
    trial_start = models.DateTimeField(null=True)
    trial_end = models.DateTimeField(null=True)

    objects = SubscriptionQuerySet.as_manager()

    @property
    def namespace_name(self):
        return self.customer.namespace_name

    def get_absolute_url(self, version):
        return reverse('subscription-detail', kwargs={
            'namespace': self.namespace_name, 'version': version, 'pk': str(self.pk)})

    def delete(self, using=None, keep_parents=False, new_status=CANCELED):
        self.canceled_at = timezone.now()
        self.ended_at = timezone.now()
        self.status = new_status
        self.save(update_fields=['canceled_at', 'ended_at', 'status'])


class InvoiceQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        user = namespace.object if namespace.type == 'user' else namespace.object.owner
        return self.filter(customer__user=user)


class Invoice(StripeModel):
    customer = models.ForeignKey(Customer)
    subscription = models.ForeignKey(Subscription, null=True, on_delete=models.CASCADE)
    amount_due = models.IntegerField()
    application_fee = models.IntegerField(null=True)
    attempt_count = models.PositiveIntegerField(null=True)
    attempted = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    currency = models.CharField(max_length=10)
    invoice_date = models.DateTimeField()
    description = models.TextField(null=True)
    next_payment_attempt = models.DateTimeField(null=True)
    paid = models.BooleanField(default=False)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    reciept_number = models.CharField(max_length=255)
    starting_balance = models.IntegerField()
    statement_descriptor = models.TextField(null=True)
    subtotal = models.IntegerField()
    tax = models.IntegerField(null=True)
    total = models.IntegerField()

    objects = InvoiceQuerySet.as_manager()

    @property
    def namespace_name(self):
        return self.customer.namespace_name

    def get_absolute_url(self, version):
        return reverse('invoice-detail', kwargs={
            'namespace': self.namespace_name, 'version': version, 'pk': str(self.pk)})


class InvoiceItemQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        user = namespace.object if namespace.type == 'user' else namespace.object.owner
        return self.filter(invoice__customer__user=user)


class InvoiceItem(StripeModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True)
    # Duplicated since in the event that a customer switches plans,
    # InvoiceItem.subscription will not equal Invoice.subscription
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True)
    amount = models.IntegerField()
    currency = models.CharField(max_length=10)
    # Nullable since this item could be for an upcoming invoice
    invoice_date = models.DateTimeField(null=True)
    proration = models.BooleanField(default=False)
    quantity = models.IntegerField()
    description = models.TextField(default="")

    objects = InvoiceItemQuerySet.as_manager()


class Charge(StripeModel):
    invoice = models.ForeignKey(Invoice)
    amount = models.PositiveIntegerField()
    amount_refunded = models.PositiveIntegerField()
    captured = models.BooleanField(default=False)
    currency = models.CharField(max_length=10)
    description = models.TextField(null=True)
    paid = models.BooleanField(default=True)
    reciept_email = models.EmailField(null=True)
    reciept_number = models.CharField(max_length=255)
    refunded = models.BooleanField(default=False)
    statement_descriptor = models.TextField(null=True)


class Coupon(StripeModel):
    amount_off = models.PositiveIntegerField(null=True)
    currency = models.CharField(max_length=255)

    FOREVER = "forever"
    ONCE = "once"
    REPEAT = "repeating"

    DURATION_CHOICES = [(FOREVER, "Forever"),
                        (ONCE, "Once"),
                        (REPEAT, "Repeat")]
    duration = models.CharField(max_length=7, choices=DURATION_CHOICES)
    # Only populated if duration is not null
    duration_in_months = models.PositiveIntegerField()
    max_redemptions = models.PositiveIntegerField()
    percent_off = models.PositiveIntegerField(null=True)
    redeem_by = models.DateTimeField(null=True)
    timed_redeemed = models.PositiveIntegerField()
    valid = models.BooleanField(default=True)


class Discount(StripeModel):
    coupon = models.ForeignKey(Coupon)
    customer = models.ForeignKey(Customer)
    # Both customer and subscription FKs are necessary despite subscription
    # Having its own FK to customer because a discount may not be applied
    # To a given description
    subscription = models.ForeignKey(Subscription, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True)
