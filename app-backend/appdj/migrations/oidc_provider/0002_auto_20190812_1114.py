# Generated by Django 2.2.1 on 2019-08-12 11:14

from django.db import migrations


def migrate_response_type(apps, schema_editor):
    RESPONSE_TYPES = [
        ('code', 'code (Authorization Code Flow)'),
        ('id_token', 'id_token (Implicit Flow)'),
        ('id_token token', 'id_token token (Implicit Flow)'),
        ('code token', 'code token (Hybrid Flow)'),
        ('code id_token', 'code id_token (Hybrid Flow)'),
        ('code id_token token', 'code id_token token (Hybrid Flow)'),
    ]
    # ensure we get proper, versioned model with the deleted response_type field;
    # importing directly yields the latest without response_type
    ResponseType = apps.get_model('oidc_provider', 'ResponseType')
    Client = apps.get_model('oidc_provider', 'Client')
    for value, description in RESPONSE_TYPES:
        ResponseType.objects.create(value=value, description=description)
    for client in Client.objects.all():
        client.response_types.add(ResponseType.objects.get(value=client.response_type))


class Migration(migrations.Migration):

    dependencies = [
        ('oidc_provider', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_response_type),
    ]