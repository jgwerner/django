import time
from django.test import TestCase

from .factories import ApplicationFactory
from ..authorization import CanvasValidator


class ValidatorTestCase(TestCase):
    def setUp(self):
        self.client_key = 'key1'
        self.validator = CanvasValidator()
        self.app = ApplicationFactory(client_id=self.client_key)

    def test_validate_timestamp_and_nonce(self):
        timestamp = time.time()
        nonce = '123456'
        self.assertTrue(self.validator.validate_timestamp_and_nonce(
            self.client_key, timestamp, nonce, None))
        self.assertFalse(self.validator.validate_timestamp_and_nonce(
            self.client_key, timestamp, nonce, None))
        self.assertFalse(self.validator.validate_timestamp_and_nonce(
            self.client_key, timestamp - 15 * 60, nonce, None))

    def test_validate_client_key(self):
        self.assertTrue(self.validator.validate_client_key(
            self.client_key, None))

    def test_get_client_secret(self):
        secret = self.validator.get_client_secret(self.client_key, None)
        self.assertEqual(secret, self.app.client_secret)
