import json

from django.urls import reverse

from rest_framework.test import APIClient


def send_register_request(*args, **kwargs):
    url = reverse("register")
    client = APIClient()
    data = {
        'username': kwargs.get('username', "test_user"),
        'password': "password",
        'email': kwargs.get('email', "test_user@example.com"),
        'profile': {}
    }
    response = client.post(url, data=json.dumps(data), content_type='application/json')
    return response
