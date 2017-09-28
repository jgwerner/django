import logging
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer as RestAuthTokenSerializer
from social_django.models import UserSocialAuth

from base.views import RequestUserMixin
from base.serializers import SearchSerializerMixin
from users.models import UserProfile, Email
User = get_user_model()
log = logging.getLogger('users')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('bio', 'url', 'location', 'company', 'timezone', 'avatar')
        read_only_fields = ('avatar',)


class UserSerializer(SearchSerializerMixin, serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'profile')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        user_exists = User.objects.filter(username=value,
                                          is_active=True).exists()
        if user_exists:
            raise serializers.ValidationError("{username} is already taken.".format(username=value))
        return value

    def create(self, validated_data):
        profile_data = {}
        if "profile" in validated_data:
            profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        user = User(**validated_data, is_active=False)
        user.set_password(password)
        user.save()
        profile = UserProfile(user=user, **profile_data)
        profile.save()
        Email.objects.create(user=user, address=validated_data['email'])
        return user

    def update(self, instance, validated_data):
        if "profile" in validated_data:
            log.info("Profile information found in update request. Setting information accordingly.")
            profile_data = validated_data.pop('profile')
            user_profile = UserProfile.objects.get(user=instance)

            for field in profile_data:
                setattr(user_profile, field, profile_data[field])

            user_profile.save()

        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)

        for field in validated_data:
            setattr(instance, field, validated_data[field])

        instance.save()

        return instance


class EmailSerializer(RequestUserMixin, serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ('id', 'address', 'public', 'unsubscribed')
        read_only_fields = ("id",)


class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSocialAuth
        fields = ('id', 'provider', 'extra_data')

    extra_data = serializers.JSONField(required=False)


class AuthTokenSerializer(RestAuthTokenSerializer):
    username = serializers.CharField(label="Username", write_only=True)
    password = serializers.CharField(label="Password", style={'input_type': 'password'}, write_only=True)
    token = serializers.CharField(label="Token", read_only=True)
