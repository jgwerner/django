import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from illumidesk.components.models import IllumiDeskBaseModel
from illumidesk.utils.subscriptions import SubscriptionModelMixin

from . import roles


class IllumiDeskTeam(SubscriptionModelMixin, IllumiDeskBaseModel):
    """
    Base team with suscriptions
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    subscription = models.ForeignKey('djstripe.Subscription', null=True, blank=True, on_delete=models.SET_NULL,
                                     help_text=_("The team's Stripe Subscription object, if it exists"))

    def __str__(self):
        return self.name

    class Meta:
        abstract = True

class Team(IllumiDeskTeam):
    """
    Customizable team
    """
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='teams', through='Membership')
    # your team customizations go here.

    def pending_invitations(self):
        return self.invitations.filter(is_accepted=False)

    @property
    def dashboard_url(self):
        return reverse('web:team_home', args=[self.slug])


class Membership(IllumiDeskBaseModel):
    """
    A user's team membership
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, choices=roles.ROLE_CHOICES)
    # your additional membership fields go here.


class Invitation(IllumiDeskBaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    role = models.CharField(max_length=100, choices=roles.ROLE_CHOICES, default=roles.ROLE_MEMBER)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='sent_invitations')
    is_accepted = models.BooleanField(default=False)
    accepted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name='accepted_invitations', null=True, blank=True)

    def get_url(self):
        return absolute_url(reverse('teams:accept_invitation', args=[self.id]))

    class Meta:
        unique_together = ('team', 'email')
