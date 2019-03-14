import logging

from django import template


logger = logging.getLogger(__name__)

register = template.Library()


def divide(value, arg):
    quotient = None
    divisor = None
    try:
        divisor = int(arg)
    except ValueError:
        logger.exception(f"Error trying to cast {arg} to an int.")
    try:
        if divisor is not None and divisor != 0:
            quotient = value / divisor
    except TypeError as e:
        logger.exception(f"Exception while attempting to use divide filter tag: {e}")
    return quotient


register.filter("divide", divide)
