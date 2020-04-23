from django.apps import AppConfig


class SubscriptionConfig(AppConfig):
    name = 'illumidesk.subscriptions'
    label = 'illumidesk_subscriptions'

    def ready(self):
        from . import webhooks
