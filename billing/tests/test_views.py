import stripe
import json
from unittest.mock import patch
from decimal import getcontext
from django.test import Client, override_settings
from django.urls import reverse
from django.conf import settings
from rest_framework import status

from billing.models import (Card,
                            Plan, Subscription,
                            Invoice, Event)
from users.tests.factories import UserFactory, EmailFactory
from billing.tests.factories import (PlanFactory,
                                     CardFactory,
                                     SubscriptionFactory,
                                     EventFactory,
                                     InvoiceFactory,
                                     InvoiceItemFactory)
from billing.tests.fake_stripe.helpers import signature_verification_error
from billing.tests import fake_stripe, BillingTestCase
from jwt_auth.utils import create_auth_jwt
import logging
log = logging.getLogger('billing')

stripe.api_key = settings.STRIPE_SECRET_KEY
getcontext().prec = 6
# TODO: Make it so that all necessary patches are condensed to one decorator or something


def create_plan_dict(trial_period=None):
    obj_dict = vars(PlanFactory.build())
    if trial_period is not None:
        obj_dict['trial_period_days'] = trial_period
    data_dict = {key: obj_dict[key] for key in obj_dict
                 if key in [f.name for f in Plan._meta.get_fields()] and key not in ["stripe_id", "created",
                                                                                     "id", "metadata"]}
    return data_dict


# @override_settings(ENABLE_BILLING=True)
class PlanTest(BillingTestCase):

    @patch("billing.stripe_utils.stripe", fake_stripe)
    def setUp(self):
        self.user = UserFactory(is_staff=True)
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_list_plans(self):
        pre_create_plan_count = Plan.objects.count()
        plan_count = 4
        PlanFactory.create_batch(plan_count)
        url = reverse("plan-list", kwargs={'namespace': self.user.username,
                                           'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), plan_count + pre_create_plan_count)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_plan_details(self):
        plan = PlanFactory()
        url = reverse("plan-detail", kwargs={'namespace': self.user.username,
                                             'pk': plan.pk,
                                             'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(plan.pk), response.data.get('id'))


# @override_settings(ENABLE_BILLING=True)
class CardTest(BillingTestCase):

    @patch("billing.stripe_utils.stripe", fake_stripe)
    def setUp(self):
        self.user = UserFactory(first_name="Foo",
                                last_name="Bar",
                                is_staff=True)
        # self.customer = create_stripe_customer_from_user(self.user)
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def _create_card_in_stripe(self):
        url = reverse("card-list", kwargs={'namespace': self.user.username,
                                           'version': settings.DEFAULT_VERSION})
        data = {'user': str(self.user.pk),
                'token': 'tok_visa'}
        self.client.post(url, data)
        card = Card.objects.get()
        return card

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_create_card(self):
        url = reverse("card-list", kwargs={'namespace': self.user.username,
                                           'version': settings.DEFAULT_VERSION})
        data = {'token': "tok_visa"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Card.objects.count(), 1)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    @patch("billing.serializers.CardSerializer.create")
    def test_stripe_errors_do_not_produce_500_error(self, mock_create):
        mock_create.side_effect = stripe.error.CardError(message="Your card's security code is incorrect.",
                                                         param="cvc_code",
                                                         code="incorrect_cvc",
                                                         http_status=status.HTTP_402_PAYMENT_REQUIRED,
                                                         json_body={'error': {'message': "Your card's security code "
                                                                                         "is incorrect.",
                                                                              'type': 'card_error',
                                                                              'param': 'cvc',
                                                                              'code': 'incorrect_cvc'}})
        url = reverse("card-list", kwargs={'namespace': self.user.username,
                                           'version': settings.DEFAULT_VERSION})
        data = {'token': "tok_cvcCheckFail"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        expected_error_data = {'message': "Your card's security code is incorrect.",
                               'type': 'card_error',
                               'param': 'cvc',
                               'code': 'incorrect_cvc'}
        self.assertDictEqual(response.data, expected_error_data)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_list_cards(self):
        not_me_card_count = 3
        for _ in range(not_me_card_count):
            user = UserFactory()
            CardFactory(customer=user.customer)
        my_card_count = 2
        CardFactory.create_batch(my_card_count, customer=self.user.customer)
        url = reverse("card-list", kwargs={'namespace': self.user.username,
                                           'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Card.objects.count(), not_me_card_count + my_card_count)
        self.assertEqual(len(response.data), my_card_count)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_card_details(self):
        card = CardFactory(customer=self.user.customer)
        url = reverse("card-detail", kwargs={'namespace': self.user.username,
                                             'pk': card.pk,
                                             'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(card.pk), response.data.get('id'))

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_card_update(self):
        card = self._create_card_in_stripe()
        url = reverse("card-detail", kwargs={'namespace': self.user.username,
                                             'pk': card.pk,
                                             'version': settings.DEFAULT_VERSION})
        data = {'name': "Mr. Foo Bar",
                'address_line1': "123 Any Street"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        card_reloaded = Card.objects.get(pk=card.pk)
        self.assertEqual(card_reloaded.name, "Mr. Foo Bar")
        self.assertEqual(card_reloaded.address_line1, "123 Any Street")

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_card_delete(self):
        card = self._create_card_in_stripe()
        url = reverse("card-detail", kwargs={'namespace': self.user.username,
                                             'pk': card.pk,
                                             'version': settings.DEFAULT_VERSION})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Card.objects.count(), 0)


# @override_settings(ENABLE_BILLING=True)
class SubscriptionTest(BillingTestCase):
    @patch("billing.stripe_utils.stripe", fake_stripe)
    def setUp(self):
        self.user = UserFactory(first_name="Foo",
                                last_name="Bar",
                                is_staff=True)
        EmailFactory(user=self.user,
                     address=self.user.email)
        # self.customer = create_stripe_customer_from_user(self.user)
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_subscription_create(self):

        pre_test_sub_count = Subscription.objects.count()
        plan = Plan.objects.get(stripe_id="threeblades-free-plan")
        url = reverse("subscription-list", kwargs={'namespace': self.user.username,
                                                   'version': settings.DEFAULT_VERSION})
        data = {'plan': plan.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.count(), pre_test_sub_count + 1)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_update_subscription_fails(self):
        subscription = SubscriptionFactory(customer=self.user.customer,
                                           status="trialing")
        url = reverse("subscription-detail", kwargs={'namespace': self.user.username,
                                                     'pk': subscription.pk,
                                                     'version': settings.DEFAULT_VERSION})
        response = self.client.patch(url, data={'status': "active"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_list_subscriptions(self):
        not_me_sub_count = 3
        for _ in range(not_me_sub_count):
            UserFactory()
            # Dont need to create a Subscription, one is created to the free plan automatically
        my_subs_count = 2
        SubscriptionFactory.create_batch(my_subs_count,
                                         customer=self.user.customer,
                                         plan__amount=500,
                                         status=Subscription.ACTIVE)
        url = reverse("subscription-list", kwargs={'namespace': self.user.username,
                                                   'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Subscription.objects.filter(customer=self.user.customer,
                                                     plan__amount__gt=0).count(), my_subs_count)
        # The + 1 here corresponds to the automatically created default subscription when the user is entered in
        # The database
        log.debug(("customer.id", self.user.customer.pk))
        log.debug(response.data)
        self.assertEqual(len(response.data), my_subs_count + 1)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_subscription_details(self):
        sub = SubscriptionFactory(customer=self.user.customer,
                                  status=Subscription.ACTIVE)
        url = reverse("subscription-detail", kwargs={'namespace': self.user.username,
                                                     'pk': sub.pk,
                                                     'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(sub.pk), response.data.get('id'))

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_subscription_cancel(self):
        subscription = Subscription.objects.get(customer=self.user.customer)
        self.assertNotEqual(subscription.status, Subscription.CANCELED)
        url = reverse("subscription-detail", kwargs={'namespace': self.user.username,
                                                     'pk': subscription.pk,
                                                     'version': settings.DEFAULT_VERSION})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        sub_reloaded = Subscription.objects.get(pk=subscription.pk)
        self.assertEqual(sub_reloaded.status, Subscription.CANCELED)
        self.assertIsNotNone(sub_reloaded.canceled_at)
        self.assertIsNotNone(sub_reloaded.ended_at)


# @override_settings(ENABLE_BILLING=True)
class InvoiceTest(BillingTestCase):

    fixtures = ['notification_types.json', "plans.json"]

    @patch("billing.stripe_utils.stripe", fake_stripe)
    def setUp(self):
        self.user = UserFactory(first_name="Foo",
                                last_name="Bar",
                                is_staff=True)
        EmailFactory(user=self.user,
                     address=self.user.email)
        token = create_auth_jwt(self.user)
        self.api_client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.client = Client()

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_invoice_items_list_is_scoped_by_invoice(self):
        first_invoice = InvoiceFactory(customer=self.user.customer)
        InvoiceItemFactory.create_batch(3, invoice=first_invoice)

        second_invoice = InvoiceFactory(customer=self.user.customer)
        InvoiceItemFactory.create_batch(2, invoice=second_invoice)

        url = reverse("invoiceitem-list", kwargs={'namespace': self.user.username,
                                                  'version': settings.DEFAULT_VERSION,
                                                  'invoice_id': str(second_invoice.id)})
        response = self.api_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        for item in response.data:
            self.assertEqual(item['invoice'], second_invoice.id)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_invoice_item_retrieve(self):
        first_invoice = InvoiceFactory(customer=self.user.customer)
        InvoiceItemFactory.create_batch(3, invoice=first_invoice)

        second_invoice = InvoiceFactory(customer=self.user.customer)
        item = InvoiceItemFactory(invoice=second_invoice)

        url = reverse("invoiceitem-detail", kwargs={'namespace': self.user.username,
                                                    'version': settings.DEFAULT_VERSION,
                                                    'invoice_id': str(second_invoice.id),
                                                    'pk': str(item.id)})
        response = self.api_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(item.id))


# @override_settings(ENABLE_BILLING=True)
class IncomingStripeWebHooksTest(BillingTestCase):

    @patch("billing.stripe_utils.stripe", fake_stripe)
    def setUp(self):
        self.user = UserFactory()

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    @patch("stripe.Webhook.construct_event")
    def test_subscription_updated_webhook(self, mock_construct):
        mock_construct.return_value = True
        url = reverse("stripe-subscription-updated", kwargs={'version': settings.DEFAULT_VERSION})
        plan = Plan.objects.get(stripe_id="threeblades-free-plan")
        subscription = SubscriptionFactory(customer=self.user.customer,
                                           plan=plan)
        webhook_data = fake_stripe.Event.get_sub_updated_evt(customer=self.user.customer.stripe_id,
                                                             subscription=subscription.stripe_id,
                                                             status=Subscription.PAST)
        response = self.client.post(url, json.dumps(webhook_data),
                                    content_type="application/json",
                                    HTTP_STRIPE_SIGNATURE="foo")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = Event.objects.filter(stripe_id=webhook_data['id'])
        self.assertEqual(events.count(), 1)
        self.assertEqual(events.first().event_type, "customer.subscription.updated")

        sub_reloaded = Subscription.objects.get(pk=subscription.pk)
        self.assertEqual(sub_reloaded.status, Subscription.PAST)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    @patch("stripe.Webhook.construct_event")
    def test_invoice_created_webhook(self, mock_construct):
        mock_construct.return_value = True
        url = reverse("stripe-invoice-created",
                      kwargs={'version': settings.DEFAULT_VERSION})
        plan = Plan.objects.get(stripe_id="threeblades-free-plan")
        subscription = SubscriptionFactory(customer=self.user.customer,
                                           plan=plan)
        webhook_data = fake_stripe.Event.get_webhook_event(event_type="invoice.created",
                                                           customer=self.user.customer.stripe_id,
                                                           plan=subscription.plan.stripe_id,
                                                           subscription=subscription.stripe_id,
                                                           amount=subscription.plan.amount,
                                                           interval=subscription.plan.interval,
                                                           trial_period=subscription.plan.trial_period_days)
        response = self.client.post(url, json.dumps(webhook_data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invoices = Invoice.objects.filter(stripe_id=webhook_data['data']['object']['id'])
        self.assertEqual(invoices.count(), 1)
        events = Event.objects.filter(stripe_id=webhook_data['id'])
        self.assertEqual(events.count(), 1)
        self.assertEqual(events.first().event_type, "invoice.created")

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    @patch("stripe.Webhook.construct_event")
    def test_invoice_payment_failed_webhook(self, mock_construct):

        mock_construct.return_value = True
        url = reverse("stripe-invoice-payment-failed",
                      kwargs={'version': settings.DEFAULT_VERSION})
        subscription = Subscription.objects.get(customer=self.user.customer)
        webhook_data = fake_stripe.Event.get_webhook_event(event_type="invoice.payment_failed",
                                                           customer=self.user.customer.stripe_id,
                                                           plan=subscription.plan.stripe_id,
                                                           subscription=subscription.stripe_id,
                                                           amount=subscription.plan.amount,
                                                           interval=subscription.plan.interval,
                                                           trial_period=subscription.plan.trial_period_days)
        response = self.client.post(url, json.dumps(webhook_data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invoices = Invoice.objects.filter(stripe_id=webhook_data['data']['object']['id'])
        self.assertEqual(invoices.count(), 1)
        events = Event.objects.filter(stripe_id=webhook_data['id'])
        self.assertEqual(events.count(), 1)
        self.assertEqual(events.first().event_type, "invoice.payment_failed")

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    @patch("stripe.Webhook.construct_event")
    def test_invoice_payment_success_webhook(self, mock_construct):
        mock_construct.return_value = True
        url = reverse("stripe-invoice-payment-success",
                      kwargs={'version': settings.DEFAULT_VERSION})
        subscription = Subscription.objects.get(customer=self.user.customer)
        webhook_data = fake_stripe.Event.get_webhook_event(event_type="invoice.payment_succeeded",
                                                           customer=self.user.customer.stripe_id,
                                                           plan=subscription.plan.stripe_id,
                                                           subscription=subscription.stripe_id,
                                                           amount=subscription.plan.amount,
                                                           interval=subscription.plan.interval,
                                                           trial_period=subscription.plan.trial_period_days)
        response = self.client.post(url, json.dumps(webhook_data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invoices = Invoice.objects.filter(stripe_id=webhook_data['data']['object']['id'])
        self.assertEqual(invoices.count(), 1)
        events = Event.objects.filter(stripe_id=webhook_data['id'])
        self.assertEqual(events.count(), 1)
        self.assertEqual(events.first().event_type, "invoice.payment_succeeded")

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    @patch("stripe.Webhook.construct_event")
    def test_sending_duplicate_event_does_nothing(self, mock_construct):
        mock_construct.return_value = True
        existing_event = EventFactory()
        url = reverse("stripe-invoice-created", kwargs={'version': settings.DEFAULT_VERSION})
        plan = Plan.objects.get(stripe_id="threeblades-free-plan")
        subscription = SubscriptionFactory(customer=self.user.customer,
                                           plan=plan)
        webhook_data = fake_stripe.Event.get_webhook_event(event_type="invoice.created",
                                                           customer=self.user.customer.stripe_id,
                                                           plan=subscription.plan.stripe_id,
                                                           subscription=subscription.stripe_id,
                                                           amount=subscription.plan.amount,
                                                           interval=subscription.plan.interval,
                                                           trial_period=subscription.plan.trial_period_days,
                                                           stripe_id=existing_event.stripe_id)
        response = self.client.post(url, json.dumps(webhook_data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        all_events = Event.objects.all()
        self.assertEqual(all_events.count(), 1)
        event_reloaded = all_events.first()
        self.assertEqual(existing_event.stripe_id, event_reloaded.stripe_id)
        self.assertEqual(event_reloaded.event_type, existing_event.event_type)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    @patch("stripe.Webhook.construct_event")
    @patch("billing.decorators.log")
    def test_construct_event_value_error(self, mock_log, mock_construct):
        mock_construct.side_effect = ValueError("foo")
        url = reverse("stripe-subscription-updated", kwargs={'version': settings.DEFAULT_VERSION})
        plan = Plan.objects.get(stripe_id="threeblades-free-plan")
        subscription = SubscriptionFactory(customer=self.user.customer,
                                           plan=plan)
        webhook_data = fake_stripe.Event.get_sub_updated_evt(customer=self.user.customer.stripe_id,
                                                             subscription=subscription.stripe_id,
                                                             status=Subscription.PAST)
        response = self.client.post(url, json.dumps(webhook_data),
                                    content_type="application/json",
                                    HTTP_STRIPE_SIGNATURE="foo")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_log.warning_assert_called_with(f"Received an invalid webhook payload at stripe_subscription_updated:")

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    @patch("stripe.Webhook.construct_event")
    @patch("billing.decorators.log")
    def test_construct_event_verification_error(self, mock_log, mock_construct):
        mock_construct.side_effect = signature_verification_error()
        url = reverse("stripe-subscription-updated", kwargs={'version': settings.DEFAULT_VERSION})
        plan = Plan.objects.get(stripe_id="threeblades-free-plan")
        subscription = SubscriptionFactory(customer=self.user.customer,
                                           plan=plan)
        webhook_data = fake_stripe.Event.get_sub_updated_evt(customer=self.user.customer.stripe_id,
                                                             subscription=subscription.stripe_id,
                                                             status=Subscription.PAST)
        response = self.client.post(url, json.dumps(webhook_data),
                                    content_type="application/json",
                                    HTTP_STRIPE_SIGNATURE="foo")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_log.warning_assert_called_with("Received an invalid webhook signature at stripe_subscription_updated:")

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    @patch("stripe.Webhook.construct_event")
    def test_subscription_updated_to_active_status(self, mock_construct):
        mock_construct.return_value = True
        url = reverse("stripe-subscription-updated", kwargs={'version': settings.DEFAULT_VERSION})
        plan = Plan.objects.get(stripe_id="threeblades-free-plan")
        subscription = SubscriptionFactory(customer=self.user.customer,
                                           plan=plan)
        webhook_data = fake_stripe.Event.get_sub_updated_evt(customer=self.user.customer.stripe_id,
                                                             subscription=subscription.stripe_id,
                                                             status=Subscription.ACTIVE)
        response = self.client.post(url, json.dumps(webhook_data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = Event.objects.filter(stripe_id=webhook_data['id'])
        self.assertEqual(events.count(), 1)
        self.assertEqual(events.first().event_type, "customer.subscription.updated")

        sub_reloaded = Subscription.objects.get(pk=subscription.pk)
        self.assertEqual(sub_reloaded.status, Subscription.ACTIVE)
        self.assertTrue(sub_reloaded.metadata.get('has_been_active', False))
