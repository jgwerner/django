import logging
import random
import string
import time
from billing import models
from .helpers import (mock_stripe_retrieve,
                      convert_db_object_to_stripe_dict)
from ..factories import (CardFactory, CustomerFactory,
                         SubscriptionFactory,
                         InvoiceItemFactory,
                         PlanFactory)
log = logging.getLogger('billing')


class FakeStripeObject:
    def __init__(self, data: dict):
        self.data = data

    def __getitem__(self, item):
        if item == "id":
            return self.data["stripe_id"]
        return self.data[item]

    def __iter__(self):
        return iter(self.data.keys())

    def __setattr__(self, key, value):
        if key == "data":
            super(FakeStripeObject, self).__setattr__(key, value)
        else:
            self.data[key] = value

    def save(self):
        return self

    def delete(self):
        self.data['status'] = "canceled"
        return self

    @classmethod
    def retrieve(cls, stripe_id):
        return cls(mock_stripe_retrieve(stripe_id))


class Customer(FakeStripeObject):
    @property
    def sources(self):
        return Sources

    @classmethod
    def create(cls, *args, **kwargs):
        customer = CustomerFactory.build(user=None)
        return convert_db_object_to_stripe_dict(customer)

    def delete(self):
        return None


class Sources(FakeStripeObject):
    @classmethod
    def create(cls, source: str):
        brand = source.replace("tok_", "").title()
        card = CardFactory.build(brand=brand)
        return convert_db_object_to_stripe_dict(card)


class Subscription(FakeStripeObject):
    @classmethod
    def create(cls, *args, **kwargs):
        plan = kwargs.get("plan")
        if isinstance(plan, str):
            plan = models.Plan.objects.get(stripe_id=plan)
            kwargs['plan'] = plan

        cus = kwargs.get("customer")
        if isinstance(cus, str):
            cus = models.Customer.objects.get(stripe_id=cus)
            kwargs['customer'] = cus

        kwargs['status'] = "active"
        sub = SubscriptionFactory.build(**kwargs)
        return convert_db_object_to_stripe_dict(sub)


class Plan(FakeStripeObject):
    @classmethod
    def create(cls, *args, **kwargs):
        if "id" in kwargs:
            kwargs['stripe_id'] = kwargs.pop("id")
        plan = PlanFactory.build(**kwargs)
        return convert_db_object_to_stripe_dict(plan)


class InvoiceItem(FakeStripeObject):

    @classmethod
    def create(cls, *args, **kwargs):
        customer = models.Customer.objects.get(stripe_id=kwargs.get("customer"))
        kwargs['customer'] = customer
        invoice = models.Invoice.objects.get(customer=customer, closed=False)
        kwargs['invoice'] = invoice
        inv_item = InvoiceItemFactory.build(**kwargs)
        return convert_db_object_to_stripe_dict(inv_item)


# TODO: Refactor this function and the Event class to make it prettier.
def generate_fake_stripe_suffix(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for _ in range(length))


class Event:
    sub_updated_webhook_obj = {"api_version": "2017-04-06",
                               "created": int(time.time()),
                               "data": {
                                   "object": {
                                       "id": "sub_{sub_id}",
                                       "object": "subscription",
                                       "application_fee_percent": None,
                                       "billing": "charge_automatically",
                                       "cancel_at_period_end": False,
                                       "canceled_at": None,
                                       "created": 1508437548,
                                       "current_period_end": 1509647148,
                                       "current_period_start": 1508437548,
                                       "customer": "cus_{cust_id}",
                                       "discount": None,
                                       "ended_at": None,
                                       "items": {
                                           "object": "list",
                                           "data": [
                                               {
                                                   "id": "si_1BEiiGLUHPUzUsaQ7Pedwx9t",
                                                   "object": "subscription_item",
                                                   "created": 1508437549,
                                                   "metadata": {
                                                   },
                                                   "plan": {
                                                       "id": "threeblades-free-plan",
                                                       "object": "plan",
                                                       "amount": 0,
                                                       "created": 1504615475,
                                                       "currency": "usd",
                                                       "interval": "month",
                                                       "interval_count": 1,
                                                       "livemode": False,
                                                       "metadata": {
                                                       },
                                                       "name": "Threeblades Free Plan",
                                                       "statement_descriptor": None,
                                                       "trial_period_days": 14
                                                   },
                                                   "quantity": 1
                                               }
                                           ],
                                           "has_more": False,
                                           "total_count": 1,
                                           "url": "/v1/subscription_items?subscription=sub_BbwbCp2WpU8F1J"
                                       },
                                       "livemode": False,
                                       "metadata": {
                                       },
                                       "plan": {
                             "id": "threeblades-free-plan",
                             "object": "plan",
                             "amount": 0,
                             "created": 1504615475,
                             "currency": "usd",
                             "interval": "month",
                             "interval_count": 1,
                             "livemode": False,
                             "metadata": {
                             },
                             "name": "Threeblades Free Plan",
                             "statement_descriptor": None,
                             "trial_period_days": 14
                         },
                                       "quantity": 1,
                                       "start": 1508437548,
                                       "status": "{sub_status}",
                                       "tax_percent": None,
                                       "trial_end": 1509647148,
                                       "trial_start": 1508437548
                                   }
                               },
                               "id": "evt_{fake}".format(fake=generate_fake_stripe_suffix(24)),
                               "livemode": False,
                               "object": "event",
                               "pending_webhooks": 0,
                               "request": {
                                   "id": "req_{fake}".format(fake=generate_fake_stripe_suffix(16)),
                                   "idempotency_key": None
                               },
                               "type": "customer.subscription.updated"
                               }
    webhook_obj = {"api_version": "2017-04-06",
                       "created": int(time.time()),
                       "data": {
                           "object": {
                               "amount_due": 0,
                               "application_fee": None,
                               "attempt_count": 0,
                               "attempted": True,
                               "charge": None,
                               "closed": True,
                               "currency": "usd",
                               "customer": "{customer.stripe_id}",
                               "date": int(time.time()),
                               "description": None,
                               "discount": None,
                               "ending_balance": 0,
                               "forgiven": False,
                               "id": "in_{fake}".format(fake=generate_fake_stripe_suffix(24)),
                               "lines": {
                                   "data": [
                                       {
                                           "amount": 0,
                                           "currency": "usd",
                                           "description": None,
                                           "discountable": True,
                                           "id": "{subscription.stripe_id}",
                                           "livemode": False,
                                           "metadata": {},
                                           "object": "line_item",
                                           "period": {
                                               "end": 1501504202,
                                               "start": int(time.time())
                                           },
                                           "plan": {
                                               "amount": "{plan.amount}",
                                               "created": 1500899401,
                                               "currency": "usd",
                                               "id": "{plan.stripe_id}",
                                               "interval": "{plan.interval}",
                                               "interval_count": 1,
                                               "livemode": False,
                                               "metadata": {},
                                               "name": "{plan.name}",
                                               "object": "plan",
                                               "statement_descriptor": "qmhZQYnrLuOa",
                                               "trial_period_days": "{plan.trial_period_days}"
                                           },
                                           "proration": False,
                                           "quantity": 1,
                                           "subscription": None,
                                           "subscription_item": "si_1Aj5hGLUHPUzUsaQAh65Brms",
                                           "type": "subscription"
                                       }
                                   ],
                                   "has_more": False,
                                   "object": "list",
                                   "total_count": 1,
                                   "url": "/v1/invoices/in_1Aj5hGLUHPUzUsaQRYfgETkt/lines"
                               },
                               "livemode": False,
                               "metadata": {},
                               "next_payment_attempt": None,
                               "object": "invoice",
                               "paid": True,
                               "period_end": int(time.time()),
                               "period_start": int(time.time()),
                               "receipt_number": None,
                               "starting_balance": 0,
                               "statement_descriptor": None,
                               "subscription": "{subscription.stripe_id}",
                               "subtotal": 0,
                               "tax": None,
                               "tax_percent": None,
                               "total": 0,
                               "webhooks_delivered_at": None
                           }
                       },
                   "id": "evt_{fake}".format(fake=generate_fake_stripe_suffix(24)),
                       "livemode": False,
                       "object": "event",
                       "pending_webhooks": 0,
                       "request": {
                           "id": "req_{fake}".format(fake=generate_fake_stripe_suffix(16)),
                           "idempotency_key": None
                       },
                       "type": "{event_type}"
                   }

    @classmethod
    def get_webhook_event(cls, *args, **kwargs):
        json = Event.webhook_obj
        json['type'] = kwargs.get("event_type")
        json['data']['object']['customer'] = kwargs.get("customer")
        json['data']['object']['subscription'] = kwargs.get("subscription")
        json['data']['object']['lines']['data'][0]['id'] = kwargs.get("subscription")
        json['data']['object']['lines']['data'][0]['plan']['id'] = kwargs.get("plan")
        json['data']['object']['lines']['data'][0]['plan']['amount'] = kwargs.get("amount")
        json['data']['object']['lines']['data'][0]['plan']['interval'] = kwargs.get("interval")
        json['data']['object']['lines']['data'][0]['plan']['trial_period_days'] = kwargs.get("trial_period")
        if kwargs.get("stripe_id") is not None:
            json['id'] = kwargs.get("stripe_id")
        return json

    @classmethod
    def get_sub_updated_evt(cls, *args, **kwargs):
        json = Event.sub_updated_webhook_obj
        json['data']['object']['id'] = kwargs.get("subscription")
        json['data']['object']['customer'] = kwargs.get("customer")
        json['data']['object']['status'] = kwargs.get("status")
        return json