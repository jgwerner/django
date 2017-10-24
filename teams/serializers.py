from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Team, Group

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    members = serializers.StringRelatedField(many=True, read_only=True, source='user_set')
    permissions = serializers.StringRelatedField(many=True)
    parent = serializers.CharField(source='get_parent', required=False)
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions', 'members', 'private', 'parent', 'created_by')

    def validate_parent(self, value):
        if not Group.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"There is no parent with id: {value}")
        return value

    def create(self, validated_data):
        team_kwarg = self.context['view'].kwargs.get('team_team')
        team = Team.objects.tbs_get(team_kwarg)
        parent = validated_data.pop('get_parent', None)
        if parent:
            parent_group = Group.objects.get(pk=parent)
            instance = parent_group.add_child(team=team, **validated_data)
        else:
            instance = Group.add_root(team=team, **validated_data)
        return instance


class TeamSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True, read_only=True)
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Team
        fields = ('id', 'name', 'description', 'website', 'location', 'groups', 'created_by')

    def validate_name(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(f"User with name {value} exists.")
        return value


class UserField(serializers.Field):
    def to_representation(self, obj):
        return obj.username

    def to_internal_value(self, data):
        try:
            user = User.objects.tbs_get(data)
        except Exception as e:
            raise serializers.ValidationError(e)
        return user


class GroupUserSerializer(serializers.Serializer):
    user = UserField()
