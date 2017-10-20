import logging
import json

from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from base.views import NamespaceMixin
from base.permissions import IsAdminUser
from billing.models import (Plan, Card, Subscription,
                            Invoice, InvoiceItem, Event)
from billing.serializers import (PlanSerializer, CardSerializer,
                                 SubscriptionSerializer,
                                 InvoiceSerializer,
                                 InvoiceItemSerializer)
from billing.stripe_utils import (handle_stripe_invoice_created,
                                  handle_upcoming_invoice,
                                  handle_stripe_invoice_payment_status_change)
from .signals import (subscription_cancelled,
                      subscription_created,
                      invoice_payment_failure)

log = logging.getLogger('billing')

if settings.MOCK_STRIPE:
    from billing.tests import mock_stripe as stripe
    log.info("Using mock_stripe module.")
else:
    import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class CardViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer

    def retrieve(self, request, *args, **kwargs):
        card = Card.objects.get(pk=kwargs.get('pk'),
                                customer__user=request.user)
        serializer = self.serializer_class(card)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        try:
            serializer.create(validated_data=request.data)
            data = serializer.data
            ret_status = status.HTTP_201_CREATED
        except stripe.error.StripeError as e:
            body = e.json_body
            error = body.get('error', {})
            log.exception(error)
            ret_status = e.http_status
            data = error

        return Response(data=data,
                        status=ret_status)

    def list(self, request, *args, **kwargs):
        cards = Card.objects.filter(customer__user=request.user)
        serializer = self.serializer_class(cards, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        # Assuming for now that we should only delete the customer record,
        # And leave the auth_user record
        instance = Card.objects.get(pk=kwargs.get('pk'))
        stripe_customer = stripe.Customer.retrieve(instance.customer.stripe_id)

        stripe_response = stripe_customer.sources.retrieve(instance.stripe_id).delete()
        instance.delete()

        data = {'stripe_id': stripe_response['id'], 'deleted': True}
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = (IsAdminUser,)


class SubscriptionViewSet(NamespaceMixin,
                          mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = Subscription.objects.all().exclude(status=Subscription.CANCELED)
    serializer_class = SubscriptionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.create(validated_data=request.data)
        subscription_created.send(sender=Subscription,
                                  user=instance.customer.user,
                                  actor=request.user,
                                  target=instance,
                                  notif_type="subscription.created")
        return Response(data=self.serializer_class(instance).data,
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = Subscription.objects.get(pk=kwargs.get('pk'))
        stripe_obj = stripe.Subscription.retrieve(instance.stripe_id)

        stripe_response = stripe_obj.delete()
        instance.delete(new_status=stripe_response['status'])

        subscription_cancelled.send(sender=Subscription,
                                    user=instance.customer.user,
                                    actor=request.user,
                                    target=instance,
                                    notif_type="subscription.canceled")

        data = {'stripe_id': stripe_response['id'], 'deleted': True}
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)


class InvoiceViewSet(NamespaceMixin,
                     viewsets.ReadOnlyModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class InvoiceItemViewSet(NamespaceMixin,
                         viewsets.ReadOnlyModelViewSet):
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(invoice_id=self.kwargs.get("invoice_id"))


@require_POST
@csrf_exempt
def stripe_invoice_created(request, *args, **kwargs):
    body = request.body
    event_json = json.loads(body.decode("utf-8"))
    handle_stripe_invoice_created(event_json)
    return HttpResponse(status=status.HTTP_200_OK)


@require_POST
@csrf_exempt
def stripe_invoice_payment_success(request, *args, **kwargs):
    body = request.body
    event_json = json.loads(body.decode("utf-8"))
    signal_data = handle_stripe_invoice_payment_status_change(event_json)

    if signal_data:
        invoice_payment_failure.send(sender=Event, **signal_data)

    return HttpResponse(status=status.HTTP_200_OK)


@require_POST
@csrf_exempt
def stripe_invoice_payment_failed(request, *args, **kwargs):
    body = request.body
    event_json = json.loads(body.decode('utf-8'))

    signal_data = handle_stripe_invoice_payment_status_change(event_json)

    if signal_data:
        invoice_payment_failure.send(sender=Event, **signal_data)

    return HttpResponse(status=status.HTTP_200_OK)


@require_POST
@csrf_exempt
def stripe_invoice_upcoming(request, *args, **kwargs):
    body = request.body
    event_json = json.loads(body.decode("utf-8"))
    handle_upcoming_invoice(event_json)

    return HttpResponse(status=status.HTTP_200_OK)
