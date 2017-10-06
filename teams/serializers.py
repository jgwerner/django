from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Team, Group

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.StringRelatedField(many=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions')


class TeamSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True, read_only=True)
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Team
        fields = ('id', 'name', 'description', 'website', 'location', 'groups', 'created_by')

    def create(self, validated_data):
        team = super().create(validated_data)
        request = self.context['request']
        owners = team.groups.create(name='owners', created_by=request.user)
        owners.user_set.add(request.user)
        return team


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
