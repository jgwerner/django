from django.test import TestCase
from ..templatetags.usd import usd
from ..templatetags.divide import divide


class TestTemplateTags(TestCase):
    def test_usd_for_int(self):
        value = usd(54)
        self.assertEqual(value, "$54.00")

    def test_usd_for_float(self):
        value = usd(54.6)
        self.assertEqual(value, "$54.60")

    def test_divide(self):
        value = divide(54, "10")
        self.assertEqual(value, 5.4)
