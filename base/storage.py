from social_django.models import UserSocialAuth, DjangoStorage


def user_exists(cls, *args, **kwargs):
    return cls.user_model().objects.filter(email=kwargs.get('email')).exists()


class CanvasDjangoStorage(DjangoStorage):
    user = User
