from rest_framework.serializers import ModelSerializer

from illumidesk.users.models import IllumiDeskUser


class UserSerializer(ModelSerializer):
    class Meta:
        model = IllumiDeskUser
        fields = ['username', 'email', 'name', 'url']

        extra_kwargs = {
            'url': {'view_name': 'api:user-detail', 'lookup_field': 'username'}
        }
