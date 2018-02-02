import logging
from django import template
log = logging.getLogger('notifications')
register = template.Library()


def usd(value):
    value_str = "$"

    if isinstance(value, int):
        value_str += str(value) + ".00"
    elif isinstance(value, float):
        parts = str(value).split(".")
        value_str += parts[0] + "." + parts[1].ljust(2, "0")

    return value_str


register.filter("usd", usd)
