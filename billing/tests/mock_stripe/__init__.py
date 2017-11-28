import time
import random
import string
import logging
from rest_framework import status
from .error import CardError
log = logging.getLogger("billing")


def generate_fake_stripe_suffix(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for _ in range(length))


class DummyStripeObj:
    def __init__(self, obj_type, json):
        self.obj_type = obj_type
        self.json = json
        self.json['id'] = self.obj_type.lower()[:2] + "_" + generate_fake_stripe_suffix(14)

    def __getattr__(self, item):
        log.debug(("item", item))
        return self.json[item]

    def __getattribute__(self, name):
        if name in ["json", "obj_type", "save", "delete"]:
            return super(DummyStripeObj, self).__getattribute__(name)
        else:
            return self.json.get(name)

    def __setattr__(self, key, value):
        if key in ["obj_type", "json"]:
            super(DummyStripeObj, self).__setattr__(key, value)
        else:
            self.json[key] = value

    def __setitem__(self, key, value):
        if key in ["obj_type", "json"]:
            self.key = value
        else:
            self.json[key] = value

    def __getitem__(self, item):
        return self.json[item]

    def __iter__(self):
        return iter(self.json.keys())

    def save(self):
        # for attr in vars(self):
        #     if attr in self.json:
        #         self.json[attr] = attr
        return self

    def delete(self):
        self.json['deleted'] = True
        return self


class Plan:
    plan = None

    @classmethod
    def create(cls, *args, **kwargs):
        mock_response = {"id": kwargs.get('name').lower().replace(" ", "-"),
                         "object": "plan",
                         "amount": kwargs.get("amount"),
                         "created": int(time.time()),
                         "currency": kwargs.get("currency"),
                         "interval": kwargs.get("interval"),
                         "interval_count": kwargs.get("interval_count"),
                         "livemode": False,
                         "metadata": {
                         },
                         "name": kwargs.get("name"),
                         "statement_descriptor": None,
                         "trial_period_days": None
                         }
        Plan.plan = DummyStripeObj("plan", mock_response)
        return Plan.plan

    @classmethod
    def retrieve(cls, stripe_id):
        if stripe_id == "threeblades-free-plan":
            raise error.InvalidRequestError
        name = stripe_id.replace("-", " ").title()
        if cls.plan is None or cls.plan['id'] != stripe_id:
            cls.plan = cls.create(id=stripe_id,
                                  object="plan",
                                  name=name,
                                  amount=0,
                                  currency="usd",
                                  interval="month",
                                  interval_count=1)
            cls.plan.json['id'] = stripe_id
        return cls.plan


class Card:
    card = None

    @classmethod
    def create(cls, *args, **kwargs):
        log.debug(("args", args, "kwargs", kwargs))
        if kwargs.get("source") == "tok_cvcCheckFail":
            raise CardError(message="Your card's security code is incorrect.",
                            param="cvc_code",
                            code="incorrect_cvc",
                            http_status=status.HTTP_402_PAYMENT_REQUIRED,
                            json_body={'error': {'message': "Your card's security code is incorrect.",
                                                 'type': 'card_error',
                                                 'param': 'cvc',
                                                 'code': 'incorrect_cvc'}})
        mock_response = {"object": "card",
                         "address_city": None,
                         "address_country": None,
                         "address_line1": None,
                         "address_line1_check": None,
                         "address_line2": None,
                         "address_state": None,
                         "address_zip": None,
                         "address_zip_check": None,
                         "brand": "MasterCard",
                         "country": "US",
                         "customer": "cus_B00PC9PKHrRTBR",
                         "cvc_check": None,
                         "dynamic_last4": None,
                         "exp_month": 8,
                         "exp_year": 2019,
                         "fingerprint": "mvikJjYyxmc4Y8E2",
                         "funding": "credit",
                         "last4": "4444",
                         "metadata": {
                         },
                         "name": None,
                         "tokenization_method": None}

        Card.card = DummyStripeObj("card", mock_response)
        return Card.card

    @classmethod
    def retrieve(cls, stripe_id):
        if cls.card is None:
            cls.card = cls.create()
            cls.card.json['id'] = stripe_id
        return cls.card


class Customer:
    customer = None
    sources = Card

    @classmethod
    def create(cls, *args, **kwargs):
        mock_response = {"account_balance": 0,
                         "created": int(time.time()),
                         "currency": None,
                         "default_source": None,
                         "delinquent": False,
                         "description": kwargs.get("description"),
                         "discount": None,
                         "email": kwargs.get("email"),
                         "id": None,
                         "livemode": False,
                         "metadata": {},
                         "object": "customer",
                         "shipping": None,
                         "sources": Card,
                         "subscriptions": {
                           "data": [],
                           "has_more": False,
                           "object": "list",
                           "total_count": 0,
                           "url": ""
                         }
                         }
        Customer.customer = DummyStripeObj("customer", mock_response)
        return Customer.customer

    @classmethod
    def retrieve(cls, stripe_id):
        if cls.customer is None:
            cls.customer = cls.create(description="foo", email="foo@example.com")
            cls.customer.json['id'] = stripe_id
        return cls.customer


class DummySubscription(DummyStripeObj):
    def delete(self):
        self.json['deleted'] = True
        self.json['status'] = "canceled"
        return self


class Subscription:
    subscription = None

    @classmethod
    def create(cls, *args, **kwargs):
        start = int(time.time())
        mock_response = {"id": "sub_B00ITnbQuwkAHz",
                         "object": "subscription",
                         "application_fee_percent": None,
                         "cancel_at_period_end": False,
                         "canceled_at": None,
                         "created": start,
                         "current_period_end": int(start * 1.1),
                         "current_period_start": start,
                         "customer": kwargs.get("customer"),
                         "discount": None,
                         "ended_at": None,
                         "items": {
                           "object": "list",
                           "data": [{}
                                    ],
                           "has_more": False,
                           "total_count": 1,
                           "url": "/v1/subscription_items?subscription=sub_B00ITnbQuwkAHz"
                         },
                         "livemode": False,
                         "metadata": {
                         },
                         "plan": {'id': kwargs.get("plan")},
                         "quantity": 1,
                         "start": start,
                         "status": "trialing",
                         "tax_percent": None,
                         "trial_end": int(start * 1.05),
                         "trial_start": start
                         }
        Subscription.subscription = DummySubscription("subscription", mock_response)
        return Subscription.subscription

    @classmethod
    def retrieve(cls, stripe_id):
        if cls.subscription is None:
            cls.subscription = cls.create()
            cls.subscription.json['id'] = stripe_id
        return cls.subscription


class Invoice:
    invoice = None

    @classmethod
    def list(cls, customer, *args, **kwargs):
        mock_response = {"id": "in_1AMLTCLUHPUzUsaQ2mk3yPHI",
                         "object": "invoice",
                         "amount_due": kwargs.get("amount_due", 1000),
                         "application_fee": None,
                         "attempt_count": 1,
                         "attempted": True,
                         "charge": "ch_1AMLTCLUHPUzUsaQrgclLeph",
                         "closed": True,
                         "currency": "usd",
                         "customer": customer,
                         "date": kwargs.get("date"),
                         "description": None,
                         "discount": None,
                         "ending_balance": 0,
                         "forgiven": False,
                         "lines": {
                           "data": [
                             {
                               "id": "",
                               "object": "line_item",
                               "amount": 14724,
                               "currency": "usd",
                               "description": None,
                               "discountable": True,
                               "livemode": True,
                               "metadata": {
                               },
                               "period": {
                                 "start": 1500291784,
                                 "end": 1531827784
                               },
                               "plan": {
                                 "id": "foo-plan",
                                 "object": "plan",
                                 "amount": 100,
                                 "created": 1496252272,
                                 "currency": "usd",
                                 "interval": "month",
                                 "interval_count": 1,
                                 "livemode": False,
                                 "metadata": {
                                 },
                                 "name": "foo plan",
                                 "statement_descriptor": None,
                                 "trial_period_days": None
                               },
                               "proration": False,
                               "quantity": 1,
                               "subscription": None,
                               "subscription_item": "si_1Ae0I8LUHPUzUsaQwnVD5xxW",
                               "type": "subscription"
                             }
                           ],
                           "total_count": 1,
                           "object": "list",
                           "url": "/v1/invoices/in_1AMLTCLUHPUzUsaQ2mk3yPHI/lines"
                         },
                         "livemode": False,
                         "metadata": {},
                         "next_payment_attempt": None,
                         "paid": True,
                         "period_end": 1495478490,
                         "period_start": 1495478490,
                         "receipt_number": None,
                         "starting_balance": 0,
                         "statement_descriptor": None,
                         "subscription": kwargs.get("subscription"),
                         "subtotal": kwargs.get("amount_due"),
                         "tax": None,
                         "tax_percent": None,
                         "total": kwargs.get("amount_due"),
                         "webhooks_delivered_at": 1495478490
                         }
        Invoice.invoice = DummyStripeObj("invoice", mock_response)
        return [Invoice.invoice]


class InvoiceItem:
    invoice_item = None

    @classmethod
    def create(cls, *args, **kwargs):
        mock_response = {"id": "ii_" + generate_fake_stripe_suffix(24),
                         "object": "invoiceitem",
                         "amount": kwargs.get("amount"),
                         "currency": kwargs.get("currency"),
                         "customer": kwargs.get("customer"),
                         "date": 1502191238,
                         "description": "3Blades Compute Usage",
                         "discountable": True,
                         "invoice": None,
                         "livemode": False,
                         "metadata": {
                         },
                         "period": {
                             "start": 1502191238,
                             "end": 1502191238
                         },
                         "plan": None,
                         "proration": False,
                         "quantity": kwargs.get("quantity"),
                         "subscription": None}
        for field in ["amount", "currency", "customer", "quantity"]:
            mock_response[field] = kwargs.get(field)

        InvoiceItem.invoice_item = DummyStripeObj("invoice_item", mock_response)
        return InvoiceItem.invoice_item


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
        json['data']['object']['lines']['data'][0]['plan']['id'] =kwargs.get("plan")
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
