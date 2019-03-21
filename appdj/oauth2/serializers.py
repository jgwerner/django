from rest_framework import serializers
from oauth2_provider.models import get_application_model

from .models import Application

ProviderApplication = get_application_model()


class ApplicationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(source='application.user', default=serializers.CurrentUserDefault())
    client_id = serializers.CharField(source='application.client_id', required=False)
    redirect_uris = serializers.CharField(source='application.redirect_uris')
    client_type = serializers.CharField(source='application.client_type')
    client_secret = serializers.CharField(source='application.client_secret', required=False)
    name = serializers.CharField(source='application.name')
    authorization_grant_type = serializers.CharField(source='application.authorization_grant_type')

    class Meta:
        model = Application
        fields = ('id', 'client_id', 'redirect_uris', 'client_type', 'client_secret',
                  'name', 'authorization_grant_type', 'user')

    def create(self, validated_data):
        pr_app = ProviderApplication.objects.create(**validated_data['application'])
        return Application.objects.create(application=pr_app)
