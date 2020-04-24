from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ReadOnlyField
from rest_framework.serializers import SlugField
from rest_framework.validators import UniqueValidator

from django.db import models

from illumidesk.teams.util import get_next_unique_team_slug
from illumidesk.users.models import IllumiDeskUser

from .models import Invitation
from .models import Membership
from .models import Team


class IllumiDeskUserSerializer(ModelSerializer):
    class Meta:
        model = IllumiDeskUser
        fields = ('first_name', 'last_name', 'get_display_name')
        abstract = True

class MembershipSerializer(ModelSerializer):
    first_name = ReadOnlyField(source='user.first_name')
    last_name = ReadOnlyField(source='user.last_name')
    display_name = ReadOnlyField(source='user.get_display_name')

    class Meta:
        model = Membership
        fields = ('id', 'first_name', 'last_name', 'display_name', 'role')


class InvitationSerializer(ModelSerializer):
    id = ReadOnlyField()
    invited_by = ReadOnlyField(source='invited_by.get_display_name')

    class Meta:
        model = Invitation
        fields = ('id', 'team', 'email', 'role', 'invited_by', 'is_accepted')


class TeamSerializer(ModelSerializer):
    slug = SlugField(
        required=False,
        validators=[UniqueValidator(queryset=Team.objects.all())],
    )
    members = MembershipSerializer(source='membership_set', many=True, read_only=True)
    invitations = InvitationSerializer(many=True, read_only=True, source='pending_invitations')
    dashboard_url = ReadOnlyField()

    class Meta:
        model = Team
        fields = ('id', 'name', 'slug', 'members', 'invitations', 'dashboard_url')

    def create(self, validated_data):
        team_name = validated_data.get("name", None)
        validated_data['slug'] = validated_data.get("slug", get_next_unique_team_slug(team_name))
        return super().create(validated_data)
