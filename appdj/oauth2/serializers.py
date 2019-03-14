from rest_framework import serializers
from oauth2_provider.models import get_application_model

from .models import Application

ProviderApplication = get_application_model()


class ApplicationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(source='application.user', default=serializers.CurrentUserDefault())
    client_id = serializers.CharField(source='application.client_id')
    redirect_uris = serializers.CharField(source='application.redirect_uris')
    client_type = serializers.CharField(source='application.client_type')
    client_secret = serializers.CharField(source='application.client_secret')
    name = serializers.CharField(source='application.name')
    authorization_grant_type = serializers.CharField(source='application.authorization_grant_type')

    class Meta:
        model = Application
        fields = ('id', 'client_id', 'redirect_uris', 'client_type', 'client_secret',
                  'name', 'authorization_grant_type', 'user')
        read_only_fields = ('client_id', 'client_secret')
