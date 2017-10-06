from rest_framework import serializers

from .models import Team, Group


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
        owners.save()
        return team
