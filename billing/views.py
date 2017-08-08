import logging
import json

from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response

from base.views import NamespaceMixin
from base.permissions import IsAdminUser
from billing.models import (Plan, Customer,
                            Card, Subscription,
                            Invoice)
from billing.serializers import (PlanSerializer, CustomerSerializer, CardSerializer,
                                 SubscriptionSerializer, InvoiceSerializer)
from billing.stripe_utils import handle_stripe_invoice_webhook, handle_upcoming_invoice


log = logging.getLogger('billing')

if settings.MOCK_STRIPE:
    from billing.tests import mock_stripe as stripe
    log.info("Using mock_stripe module.")
else:
    import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class CustomerViewSet(viewsets.ModelViewSet):

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def list(self, request, *args, **kwargs):
        queryset = Customer.objects.filter(user=request.user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        # Assuming for now that we should only delete the customer record,
        # And leave the auth_user record
        instance = Customer.objects.get(pk=kwargs.get('pk'))
        stripe_obj = stripe.Customer.retrieve(instance.stripe_id)

        stripe_response = stripe_obj.delete()
        instance.delete()

        data = {'stripe_id': stripe_response['id'], 'deleted': True}
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)


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
        instance = serializer.create(validated_data=request.data)
        return Response(data=self.serializer_class(instance).data,
                        status=status.HTTP_201_CREATED)

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


class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = (IsAdminUser,)

    def destroy(self, request, *args, **kwargs):
        instance = Plan.objects.get(pk=kwargs.get('pk'))
        stripe_obj = stripe.Plan.retrieve(instance.stripe_id)

        stripe_response = stripe_obj.delete()
        instance.delete()

        data = {'stripe_id': stripe_response['id'], 'deleted': True}
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(NamespaceMixin,
                          viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.create(validated_data=request.data)
        return Response(data=self.serializer_class(instance).data,
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = Subscription.objects.get(pk=kwargs.get('pk'))
        stripe_obj = stripe.Subscription.retrieve(instance.stripe_id)

        stripe_response = stripe_obj.delete()
        instance.canceled_at = timezone.now()
        instance.ended_at = timezone.now()
        instance.status = stripe_response['status']
        instance.save()

        data = {'stripe_id': stripe_response['id'], 'deleted': True}
        return Response(data=data, status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
def no_subscription(request, *args, **kwargs):
    return Response(status=status.HTTP_402_PAYMENT_REQUIRED)


class InvoiceViewSet(NamespaceMixin,
                     viewsets.ReadOnlyModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


@require_POST
@csrf_exempt
def stripe_invoice_created(request, *args, **kwargs):
    body = request.body
    event_json = json.loads(body.decode("utf-8"))
    handle_stripe_invoice_webhook(event_json)
    return HttpResponse(status=status.HTTP_200_OK)


@require_POST
@csrf_exempt
def stripe_invoice_upcoming(request, *args, **kwargs):
    body = request.body
    event_json = json.loads(body.decode("utf-8"))
    # TODO: Think about how to return 200 OK before doing this calculation
    handle_upcoming_invoice(event_json)

    return HttpResponse(status=status.HTTP_200_OK)
