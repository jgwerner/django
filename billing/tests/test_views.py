import json
from decimal import Decimal, getcontext
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import (Card,
                            Plan, Subscription,
                            Invoice, Event, InvoiceItem)
from users.tests.factories import UserFactory, EmailFactory
from projects.tests.factories import CollaboratorFactory
from servers.tests.factories import ServerRunStatisticsFactory
from billing.tests.factories import (PlanFactory,
                                     CardFactory,
                                     SubscriptionFactory,
                                     EventFactory,
                                     InvoiceFactory,
                                     InvoiceItemFactory)
from billing.stripe_utils import create_stripe_customer_from_user, create_plan_in_stripe


if settings.MOCK_STRIPE:
    from billing.tests import mock_stripe as stripe
else:
    import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
getcontext().prec = 6


def create_plan_dict(trial_period=None):
    obj_dict = vars(PlanFactory.build())
    if trial_period is not None:
        obj_dict['trial_period_days'] = trial_period
    data_dict = {key: obj_dict[key] for key in obj_dict
                 if key in [f.name for f in Plan._meta.get_fields()] and key not in ["stripe_id", "created",
                                                                                     "id", "metadata"]}
    return data_dict


class PlanTest(APITestCase):
    def setUp(self):
        self.user = UserFactory(is_staff=True)
        self.token_header = "Token {auth}".format(auth=self.user.auth_token.key)
        self.client = self.client_class(HTTP_AUTHORIZATION=self.token_header)
        self.plans_to_delete = []

    def tearDown(self):
        for plan in self.plans_to_delete:
            stripe_obj = stripe.Plan.retrieve(plan.stripe_id)
            stripe_obj.delete()

    def test_list_plans(self):
        pre_create_plan_count = Plan.objects.count()
        plan_count = 4
        plans = PlanFactory.create_batch(plan_count)
        url = reverse("plan-list", kwargs={'namespace': self.user.username,
                                           'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), plan_count + pre_create_plan_count)

    def test_plan_details(self):
        plan = PlanFactory()
        url = reverse("plan-detail", kwargs={'namespace': self.user.username,
                                             'pk': plan.pk,
                                             'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(plan.pk), response.data.get('id'))


class CardTest(APITestCase):
    def setUp(self):
        self.user = UserFactory(first_name="Foo",
                                last_name="Bar",
                                is_staff=True)
        self.customer = create_stripe_customer_from_user(self.user)
        self.token_header = "Token {auth}".format(auth=self.user.auth_token.key)
        self.client = self.client_class(HTTP_AUTHORIZATION=self.token_header)

    def tearDown(self):
        stripe_obj = stripe.Customer.retrieve(self.customer.stripe_id)
        stripe_obj.delete()

    def _create_card_in_stripe(self):
        url = reverse("card-list", kwargs={'namespace': self.user.username,
                                           'version': settings.DEFAULT_VERSION})
        data = {'user': str(self.user.pk),
                'token': 'tok_visa'}
        self.client.post(url, data)
        card = Card.objects.get()
        return card

    def test_create_card(self):
        url = reverse("card-list", kwargs={'namespace': self.user.username,
                                           'version': settings.DEFAULT_VERSION})
        data = {'token': "tok_visa"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Card.objects.count(), 1)

    def test_stripe_errors_do_not_produce_500_error(self):
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

    def test_list_cards(self):
        not_me_card_count = 3
        for _ in range(not_me_card_count):
            user = UserFactory()
            CardFactory(customer=user.customer)
        my_card_count = 2
        my_cards = CardFactory.create_batch(my_card_count, customer=self.customer)
        url = reverse("card-list", kwargs={'namespace': self.user.username,
                                           'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Card.objects.count(), not_me_card_count + my_card_count)
        self.assertEqual(len(response.data), my_card_count)

    def test_card_details(self):
        card = CardFactory(customer=self.customer)
        url = reverse("card-detail", kwargs={'namespace': self.user.username,
                                             'pk': card.pk,
                                             'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(card.pk), response.data.get('id'))

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

    def test_card_delete(self):
        card = self._create_card_in_stripe()
        url = reverse("card-detail", kwargs={'namespace': self.user.username,
                                             'pk': card.pk,
                                             'version': settings.DEFAULT_VERSION})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Card.objects.count(), 0)


class SubscriptionTest(APITestCase):
    fixtures = ['notification_types.json']

    def setUp(self):
        self.user = UserFactory(first_name="Foo",
                                last_name="Bar",
                                is_staff=True)
        EmailFactory(user=self.user,
                     address=self.user.email)
        self.customer = create_stripe_customer_from_user(self.user)
        self.token_header = "Token {auth}".format(auth=self.user.auth_token.key)
        self.client = self.client_class(HTTP_AUTHORIZATION=self.token_header)
        self.plans_to_delete = []

    def tearDown(self):
        stripe_obj = stripe.Customer.retrieve(self.customer.stripe_id)
        stripe_obj.delete()

        for plan in self.plans_to_delete:
            stripe_obj = stripe.Plan.retrieve(plan.stripe_id)
            stripe_obj.delete()

    def _create_plan_in_stripe(self, trial_period=None):
        plan_data = create_plan_dict(trial_period)
        plan = create_plan_in_stripe(plan_data)
        plan.save()
        self.plans_to_delete.append(plan)
        return plan

    def _create_subscription_in_stripe(self, trial_period=7):
        plan = self._create_plan_in_stripe(trial_period)
        url = reverse("subscription-list", kwargs={'namespace': self.user.username,
                                                   'version': settings.DEFAULT_VERSION})
        data = {'plan': plan.pk}
        self.client.post(url, data)

        subscription = Subscription.objects.get(plan=plan)
        return subscription

    def test_subscription_create(self):
        pre_test_sub_count = Subscription.objects.count()
        plan = self._create_plan_in_stripe(trial_period=7)
        url = reverse("subscription-list", kwargs={'namespace': self.user.username,
                                                   'version': settings.DEFAULT_VERSION})
        data = {'plan': plan.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.count(), pre_test_sub_count + 1)

    def test_update_subscription_fails(self):
        subscription = SubscriptionFactory(customer=self.customer,
                                           status="trialing")
        url = reverse("subscription-detail", kwargs={'namespace': self.user.username,
                                                     'pk': subscription.pk,
                                                     'version': settings.DEFAULT_VERSION})
        response = self.client.patch(url, data={'status': "active"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list_subscriptions(self):
        not_me_sub_count = 3
        for _ in range(not_me_sub_count):
            UserFactory()
            # Dont need to create a Subscription, one is created to the free plan automatically
        my_subs_count = 2
        SubscriptionFactory.create_batch(my_subs_count, customer=self.customer,
                                         status=Subscription.ACTIVE)
        url = reverse("subscription-list", kwargs={'namespace': self.user.username,
                                                   'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Subscription.objects.filter(plan__amount__gt=0).count(), my_subs_count)
        self.assertEqual(len(response.data), my_subs_count)

    def test_subscription_details(self):
        sub = SubscriptionFactory(customer=self.customer,
                                  status=Subscription.ACTIVE)
        url = reverse("subscription-detail", kwargs={'namespace': self.user.username,
                                                     'pk': sub.pk,
                                                     'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(sub.pk), response.data.get('id'))

    def test_subscription_cancel(self):
        pre_test_sub_count = Subscription.objects.count()
        subscription = self._create_subscription_in_stripe()
        url = reverse("subscription-detail", kwargs={'namespace': self.user.username,
                                                     'pk': subscription.pk,
                                                     'version': settings.DEFAULT_VERSION})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Subscription.objects.count(), pre_test_sub_count + 1)
        sub_reloaded = Subscription.objects.get(pk=subscription.pk)
        self.assertEqual(sub_reloaded.status, Subscription.CANCELED)
        self.assertIsNotNone(sub_reloaded.canceled_at)
        self.assertIsNotNone(sub_reloaded.ended_at)


class InvoiceTest(TestCase):

    def setUp(self):
        self.user = UserFactory(first_name="Foo",
                                last_name="Bar",
                                is_staff=True)
        self.customer = create_stripe_customer_from_user(self.user)
        self.token_header = "Token {auth}".format(auth=self.user.auth_token.key)
        self.token_header = "Token {auth}".format(auth=self.user.auth_token.key)
        self.api_client = self.client_class(HTTP_AUTHORIZATION=self.token_header)
        self.client = Client()
        self.plans_to_delete = []

    def tearDown(self):
        stripe_obj = stripe.Customer.retrieve(self.customer.stripe_id)
        stripe_obj.delete()

        for plan in self.plans_to_delete:
            stripe_obj = stripe.Plan.retrieve(plan.stripe_id)
            stripe_obj.delete()

    def _create_plan_in_stripe(self, trial_period=None):
        plan_data = create_plan_dict(trial_period)
        plan = create_plan_in_stripe(plan_data)
        plan.save()
        self.plans_to_delete.append(plan)
        return plan

    def _create_subscription_in_stripe(self, trial_period=7):
        plan = self._create_plan_in_stripe(trial_period)
        url = reverse("subscription-list", kwargs={'namespace': self.user.username,
                                                   'version': settings.DEFAULT_VERSION})
        data = {'plan': str(plan.pk)}
        self.api_client.post(url, json.dumps(data), content_type="application/json")

        subscription = Subscription.objects.get(plan=plan)
        return subscription

    def test_invoice_items_list_is_scoped_by_invoice(self):
        first_invoice = InvoiceFactory(customer=self.customer)
        InvoiceItemFactory.create_batch(3, invoice=first_invoice)

        second_invoice = InvoiceFactory(customer=self.customer)
        InvoiceItemFactory.create_batch(2, invoice=second_invoice)

        url = reverse("invoiceitem-list", kwargs={'namespace': self.user.username,
                                                  'version': settings.DEFAULT_VERSION,
                                                  'invoice_id': str(second_invoice.id)})
        response = self.api_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        for item in response.data:
            self.assertEqual(item['invoice'], second_invoice.id)

    def test_invoice_item_retrieve(self):
        first_invoice = InvoiceFactory(customer=self.customer)
        InvoiceItemFactory.create_batch(3, invoice=first_invoice)

        second_invoice = InvoiceFactory(customer=self.customer)
        item = InvoiceItemFactory(invoice=second_invoice)

        url = reverse("invoiceitem-detail", kwargs={'namespace': self.user.username,
                                                    'version': settings.DEFAULT_VERSION,
                                                    'invoice_id': str(second_invoice.id),
                                                    'pk': str(item.id)})
        response = self.api_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(item.id))

    def test_invoice_created_webhook(self):
        url = reverse("stripe-invoice-created",
                      kwargs={'version': settings.DEFAULT_VERSION})
        # Always use Mock stripe for these tests, configuring webhooks for testing is near impossible.
        from billing.tests import mock_stripe
        subscription = self._create_subscription_in_stripe()
        webhook_data = mock_stripe.Event.get_webhook_event(event_type="invoice.created",
                                                           customer=self.customer.stripe_id,
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

    def test_invoice_payment_failed_webhook(self):
        url = reverse("stripe-invoice-created",
                      kwargs={'version': settings.DEFAULT_VERSION})
        # Always use Mock stripe for these tests, configuring webhooks for testing is near impossible.
        from billing.tests import mock_stripe
        subscription = self._create_subscription_in_stripe()
        webhook_data = mock_stripe.Event.get_webhook_event(event_type="invoice.payment_failed",
                                                           customer=self.customer.stripe_id,
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
        sub_reloaded = Subscription.objects.get(pk=subscription.pk)
        stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_id)
        self.assertEqual(sub_reloaded.status, stripe_subscription['status'])

    def test_invoice_upcoming_webhook(self):
        url = reverse("stripe-invoice-upcoming", kwargs={'version': settings.DEFAULT_VERSION})
        from billing.tests import mock_stripe
        subscription = self._create_subscription_in_stripe()

        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        run_stats = ServerRunStatisticsFactory(server__project=project)

        expected_cost = (run_stats.server.server_size.cost_per_second *
                         Decimal((run_stats.stop - run_stats.start).total_seconds())) * 100

        webhook_data = mock_stripe.Event.get_webhook_event(event_type="invoice.upcoming",
                                                           customer=self.customer.stripe_id,
                                                           plan=subscription.plan.stripe_id,
                                                           subscription=subscription.stripe_id,
                                                           amount=subscription.plan.amount,
                                                           interval=subscription.plan.interval,
                                                           trial_period=subscription.plan.trial_period_days)
        response = self.client.post(url, json.dumps(webhook_data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        events = Event.objects.filter(stripe_id=webhook_data['id'])
        self.assertEqual(events.count(), 1)
        self.assertEqual(events.first().event_type, "invoice.upcoming")

        # Note: Normally we would want to ensure that the invoice item was associated with the correct
        # Invoice, but since the Invoice is still upcoming, it is not stored in our DB, thus the Item
        # Has no association yet.
        invoice_items = InvoiceItem.objects.all()
        self.assertEqual(invoice_items.count(), 1)
        self.assertEqual(invoice_items.first().amount, expected_cost)

    def test_sending_duplicate_event_does_nothing(self):
        existing_event = EventFactory()
        from billing.tests import mock_stripe
        url = reverse("stripe-invoice-created", kwargs={'version': settings.DEFAULT_VERSION})
        subscription = self._create_subscription_in_stripe()
        webhook_data = mock_stripe.Event.get_webhook_event(event_type="invoice.created",
                                                           customer=self.customer.stripe_id,
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
