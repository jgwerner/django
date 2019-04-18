from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
UserModel = get_user_model()


class ActiveUserBackend(ModelBackend):
    """
       Custom authentication backend that is identical to Django's
       default authentication backend, except that it only searches
       among active users when authenticating.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel.objects.get(username=username,
                                         is_active=True)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
