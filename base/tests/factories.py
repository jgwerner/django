import factory
import random
import string
from factory import fuzzy


class FuzzyEmail(fuzzy.BaseFuzzyAttribute):
    def __init__(self, *args, **kwargs):
        super(FuzzyEmail, self).__init__()

    def fuzz(self):
        prefix = "".join(random.choices(string.ascii_letters + string.digits, k=239))

        # suffix = domain.TLD, e.d. 3blades.io
        suffix = ("".join(random.choices(string.ascii_letters, k=10)) +
                  "." + "".join(random.choices(string.ascii_letters, k=3)))
        email = prefix + "@" + suffix
        return email
