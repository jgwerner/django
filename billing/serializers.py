import logging
from django.db import transaction
from django.conf import settings
from rest_framework import serializers

from billing.models import (Card, Plan, Subscription,
                            Invoice, InvoiceItem)
from billing.stripe_utils import (convert_stripe_object,
                                  create_subscription_in_stripe,
                                  create_card_in_stripe)
log = logging.getLogger('billing')
if settings.MOCK_STRIPE:
    from billing.tests import mock_stripe as stripe
    log.info("Using mock_stripe module.")
else:
    import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"
        read_only_fields = ('stripe_id', 'created')


class CardSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, required=False)
    address_line1 = serializers.CharField(max_length=255, required=False)
    address_line2 = serializers.CharField(max_length=255, required=False)
    address_city = serializers.CharField(max_length=255, required=False)
    address_state = serializers.CharField(max_length=100, required=False)
    address_zip = serializers.CharField(max_length=15, required=False)
    address_country = serializers.CharField(max_length=255, required=False)
    exp_month = serializers.IntegerField(min_value=1, max_value=12, required=False)
    exp_year = serializers.IntegerField(required=False)

    token = serializers.CharField(max_length=255, required=False, allow_blank=True)

    # Begin read-only fields
    id = serializers.UUIDField(read_only=True)
    address_line1_check = serializers.CharField(read_only=True)
    address_zip_check = serializers.CharField(read_only=True)
    brand = serializers.CharField(read_only=True)
    cvc_check = serializers.CharField(read_only=True)
    last4 = serializers.CharField(read_only=True)
    fingerprint = serializers.CharField(read_only=True)
    funding = serializers.CharField(read_only=True)
    stripe_id = serializers.CharField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    customer = serializers.CharField(source='customer.user', read_only=True) # returns username instead of id

    def create(self, validated_data):
        return create_card_in_stripe(validated_data,
                                     user=self.context['request'].user)

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                customer = instance.customer
                stripe_customer = stripe.Customer.retrieve(customer.stripe_id)
                stripe_card = stripe_customer.sources.retrieve(instance.stripe_id)

                for key in validated_data:
                    setattr(stripe_card, key, validated_data[key])

                stripe_resp = stripe_card.save()
                converted_data = convert_stripe_object(Card, stripe_resp)

                for key in converted_data:
                    setattr(instance, key, converted_data[key])

                instance.save()
                return instance
        except Exception as e:
            log.exception(e)


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("id", "plan", 'stripe_id', 'created', 'livemode', 'application_fee_percent',
                  'cancel_at_period_end', 'canceled_at', 'current_period_start',
                  'current_period_end', 'start', 'ended_at', 'quantity', 'status',
                  'trial_start', 'trial_end', 'customer')
        read_only_fields = ('stripe_id', 'created', 'livemode', 'application_fee_percent',
                            'cancel_at_period_end', 'canceled_at', 'current_period_start',
                            'current_period_end', 'start', 'ended_at', 'quantity', 'status',
                            'trial_start', 'trial_end', 'customer')

    def create(self, validated_data):
        return create_subscription_in_stripe(validated_data,
                                             user=self.context['request'].user)


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = "__all__"
