import logging
from django import template
log = logging.getLogger('notifications')
register = template.Library()


def divide(value, arg):
    quotient = None
    divisor = None
    try:
        divisor = int(arg)
    except ValueError:
        log.exception(f"Error trying to cast {arg} to an int.")
    try:
        if divisor is not None and divisor != 0:
            quotient = value / divisor
    except TypeError as e:
        log.exception(f"Exception while attempting to use divide filter tag: {e}")
    return quotient

register.filter("divide", divide)
