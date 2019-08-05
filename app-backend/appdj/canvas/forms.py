from django import forms


class JWTForm(forms.Form):
    id_token = forms.CharField(max_length=100000)
    utf8 = forms.BooleanField(required=False)
    commit = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=32, required=False)
