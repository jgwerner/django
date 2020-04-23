from django import forms
from django.contrib.auth.forms import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import IllumiDeskUser


User = get_user_model()


class UserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class UserCreationForm(UserCreationForm):

    error_message = UserCreationForm.error_messages.update(
        {'duplicate_username': _('This username has already been taken.')}
    )

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data['username']

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(self.error_messages['duplicate_username'])


class IllumiDeskUserChangeForm(UserChangeForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = IllumiDeskUser
        fields = ('email', 'first_name', 'last_name')


class UploadAvatarForm(forms.Form):
    avatar = forms.FileField()
