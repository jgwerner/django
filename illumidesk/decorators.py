from stripe.error import CardError

from django.http import JsonResponse


class catch_stripe_errors:
    """
    Meant to be used with django views only.
    """
    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        try:
            return self.f(*args, **kwargs)
        except CardError as e:
            return JsonResponse({
                'error': {
                    'message': e._message,
                }
            }, status=400)
