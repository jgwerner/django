# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-25 12:38
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import social_django.fields
import social_django.storage
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Association',
            fields=[
                ('server_url', models.CharField(max_length=255)),
                ('handle', models.CharField(max_length=255)),
                ('secret', models.CharField(max_length=255)),
                ('issued', models.IntegerField()),
                ('lifetime', models.IntegerField()),
                ('assoc_type', models.CharField(max_length=64)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'social_auth_association',
            },
            bases=(models.Model, social_django.storage.DjangoAssociationMixin),
        ),
        migrations.CreateModel(
            name='Code',
            fields=[
                ('email', models.EmailField(max_length=254)),
                ('code', models.CharField(db_index=True, max_length=32)),
                ('verified', models.BooleanField(default=False)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'social_auth_code',
            },
            bases=(models.Model, social_django.storage.DjangoCodeMixin),
        ),
        migrations.CreateModel(
            name='Nonce',
            fields=[
                ('server_url', models.CharField(max_length=255)),
                ('timestamp', models.IntegerField()),
                ('salt', models.CharField(max_length=65)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'social_auth_nonce',
            },
            bases=(models.Model, social_django.storage.DjangoNonceMixin),
        ),
        migrations.CreateModel(
            name='Partial',
            fields=[
                ('token', models.CharField(db_index=True, max_length=32)),
                ('next_step', models.PositiveSmallIntegerField(default=0)),
                ('backend', models.CharField(max_length=32)),
                ('data', social_django.fields.JSONField(default={})),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'social_auth_partial',
            },
            bases=(models.Model, social_django.storage.DjangoPartialMixin),
        ),
        migrations.CreateModel(
            name='UserSocialAuth',
            fields=[
                ('provider', models.CharField(max_length=32)),
                ('uid', models.CharField(max_length=255)),
                ('extra_data', social_django.fields.JSONField(default={})),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_auth', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'social_auth_usersocialauth',
            },
            bases=(models.Model, social_django.storage.DjangoUserMixin),
        ),
        migrations.AlterUniqueTogether(
            name='nonce',
            unique_together=set([('server_url', 'timestamp', 'salt')]),
        ),
        migrations.AlterUniqueTogether(
            name='code',
            unique_together=set([('email', 'code')]),
        ),
        migrations.AlterUniqueTogether(
            name='association',
            unique_together=set([('server_url', 'handle')]),
        ),
        migrations.AlterUniqueTogether(
            name='usersocialauth',
            unique_together=set([('provider', 'uid')]),
        ),
    ]