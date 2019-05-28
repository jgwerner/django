import os

from django.conf import settings
from djoser.email import ActivationEmail, ConfirmationEmail, PasswordResetEmail

# from config.settings import Base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CustomActivationEmail(ActivationEmail):
    """
    Custom Djoser email handler to use a custom activation email template.
    """
    template_name = os.path.join(BASE_DIR, 'users/templates/email/activation.html')


class CustomConfirmationEmail(ConfirmationEmail):
    """
    Custom Djoser email handler to use a custom confirmation email template.
    """
    template_name = os.path.join(BASE_DIR, 'users/templates/email/confirmation.html')


class CustomPasswordResetEmail(PasswordResetEmail):
    """
    Custom Djoser email handler to use a custom password reset email template.
    """
    template_name = os.path.join(BASE_DIR, 'users/templates/email/password_reset.html')

    def get_context_data(self):
        context = super().get_context_data()

        context['password_reset_domain'] = settings.DJOSER['PASSWORD_RESET_DOMAIN'].format(**context)
        return context
