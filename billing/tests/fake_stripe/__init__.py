import logging
from billing import models
from .helpers import (mock_stripe_retrieve,
                      convert_db_object_to_stripe_dict)
from ..factories import (CardFactory, CustomerFactory,
                         SubscriptionFactory,
                         InvoiceItemFactory)
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
    pass


class InvoiceItem(FakeStripeObject):

    @classmethod
    def create(cls, *args, **kwargs):
        customer = models.Customer.objects.get(stripe_id=kwargs.get("customer"))
        kwargs['customer'] = customer
        invoice = models.Invoice.objects.get(customer=customer, closed=False)
        kwargs['invoice'] = invoice
        inv_item = InvoiceItemFactory.build(**kwargs)
        return convert_db_object_to_stripe_dict(inv_item)
