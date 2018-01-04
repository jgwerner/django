from .helpers import (mock_stripe_retrieve,
                      convert_db_object_to_stripe_dict)
from ..factories import CardFactory


class FakeStripeObject:
    def __init__(self, data: dict):
        self.data = data

    def __getitem__(self, item):
        return self.data[item]

    def __iter__(self):
        return iter(self.data.keys())

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


class Sources(FakeStripeObject):
    @classmethod
    def create(cls, source: str):
        brand = source.replace("tok_", "").title()
        card = CardFactory.build(brand=brand)
        return convert_db_object_to_stripe_dict(card)
