import hashlib

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models import FileField
from django.db.models import ForeignKey
from django.db.models import SET_NULL
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from illumidesk.utils.subscriptions import SubscriptionModelMixin


class IllumiDeskBaseUser(SubscriptionModelMixin, AbstractUser):
    """
    Abstract base class for users, with a small amount of added functionality
    """
    avatar = FileField(upload_to='profile-pictures/', null=True, blank=True)
    customer = ForeignKey('djstripe.Customer', null=True, blank=True, on_delete=SET_NULL,
                                 help_text=_("The user's Stripe Customer object, if it exists"))
    # todo: this is only used in a user install, but leaving for now to unify migrations between users and teams
    subscription = ForeignKey('djstripe.Subscription', null=True, blank=True, on_delete=SET_NULL,
                                     help_text=_("The user's Stripe Subscription object, if it exists"))

    class Meta:
        abstract = True

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def get_display_name(self):
        if self.get_full_name().strip():
            return self.get_full_name()
        return self.email

    @property
    def avatar_url(self):
        default_avatar_image = 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/User_font_awesome.svg/512px-User_font_awesome.svg.png'
        if self.avatar:
            return self.avatar.url
        else:
            return 'https://www.gravatar.com/avatar/{}?s=128&d={}'.format(self.gravatar_id, default_avatar_image)

    @property
    def gravatar_id(self):
        # https://en.gravatar.com/site/implement/hash/
        return hashlib.md5(self.email.lower().strip().encode('utf-8')).hexdigest()


class IllumiDeskUser(IllumiDeskBaseUser):
    """
    Add additional fields to the user model here.
    """
