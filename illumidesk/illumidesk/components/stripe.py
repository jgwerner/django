from django.conf import settings


def get_stripe_public_key():
    return settings.STRIPE_LIVE_PUBLIC_KEY if settings.STRIPE_LIVE_MODE else settings.STRIPE_TEST_PUBLIC_KEY


def get_stripe_secret_key():
    return settings.STRIPE_LIVE_SECRET_KEY if settings.STRIPE_LIVE_MODE else settings.STRIPE_TEST_SECRET_KEY
